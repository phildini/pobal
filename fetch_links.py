from datetime import (
    datetime,
    timedelta,
)
import jinja2
import json
import os
import os.path
import pytz
import requests
import tweepy
import warnings

from bs4 import BeautifulSoup


def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s env variable" % var_name
        raise EnvironmentError(error_msg)


def get_yesterday():
    tz = pytz.timezone("America/New_York")
    yesterday = datetime.now(tz).date() - timedelta(days=1)
    return yesterday


def get_sorted_status_links():
    if not os.path.isfile("tweets.json"):
        auth = tweepy.OAuthHandler(
            get_env_variable('TWITTER_KEY'),
            get_env_variable('TWITTER_SECRET'),
        )
        auth.set_access_token(
            get_env_variable('TWITTER_TOKEN'),
            get_env_variable('TWITTER_TOKEN_SECRET'),
        )

        api = tweepy.API(auth)
        api.home_timeline()
        statuses = [status._json for status in api.home_timeline(count=500)]
        statuses_with_links = [status for status in statuses if status['entities'] and status['entities']['urls']]
        for status in statuses_with_links:
            status['weight'] = float(
                status['favorite_count']
            ) * 0.5 + float(
                status['retweet_count']
            )

        sorted_statuses = sorted(
            statuses_with_links,
            key=lambda status: status.get('weight'),
            reverse=True,
        )

        with open('tweets.json', 'w') as tweets:
            json.dump(sorted_statuses, tweets)

    else:
        with open('tweets.json') as tweets:
            json_data = tweets.read()
            sorted_statuses = json.loads(json_data)

    link_objects_to_export = []
    links = []
    for status in sorted_statuses:

        link = status['entities']['urls'][0]['expanded_url']
        if link in links:
            sorted_statuses.remove(status)
            continue
        else:
            links.append(link)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                page = requests.get(link, verify=False)
            except:
                page = None
        if page and page.status_code == 200:
            soup = BeautifulSoup(page.text)
            try:
                link_title = soup.title.string
            except AttributeError:
                link_title = link
            link_object = [{
                'link': link,
                'link_text': link_title,
                'tweet_id': status['id'],
                'tweet_text': status['text'],
                'tweet_link': "https://www.twitter.com/%s/status/%s" % (
                    status['user']['screen_name'], status['id_str']
                ),
            }]
            link_objects_to_export += link_object
    return link_objects_to_export


def render_link_page(link_objects):
    template_loader = jinja2.FileSystemLoader('.')
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template('template.html')
    template_vars = {
        "links": link_objects,
    }

    yesterday = get_yesterday()
    if os.path.isfile("%s/%s.html" % (
        get_env_variable('TWEET_HTML_PATH'),
        yesterday,
    )):
        template_vars['previous'] = yesterday

    index_html_path = "%s/index.html" % (get_env_variable('TWEET_HTML_PATH'))
    with open(index_html_path, 'w') as html:
        html.write(template.render(template_vars).encode('utf-8'))


if __name__ == "__main__":
    render_link_page(get_sorted_status_links())
