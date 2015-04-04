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
import warnings
import urllib
import imp

from requests_oauthlib import OAuth1
import settings

from bs4 import BeautifulSoup

try:
    imp.find_module('local_settings')
    import local_settings
    config = local_settings
except ImportError:
    config = settings

def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s env variable" % var_name
        raise EnvironmentError(error_msg)


def get_yesterday():
    tz = pytz.timezone(settings.TIMEZONE)
    yesterday = datetime.now(tz).date() - timedelta(days=1)
    return yesterday


def get_sorted_status_links():
    auth = OAuth1(
        get_env_variable('TWITTER_KEY'),
        get_env_variable('TWITTER_SECRET'),
        get_env_variable('TWITTER_TOKEN'),
        get_env_variable('TWITTER_TOKEN_SECRET'),
    )
    parameters = {'count': config.TWEETS_TO_FETCH}
    url = config.TWITTER_HOME_URL
    if config.TWITTER_USERS:
        users_string = ''
        for idx, user in enumerate(config.TWITTER_USERS):
            users_string += "from:%s" % (user)
            if idx < len(config.TWITTER_USERS) - 1:
                users_string += ' OR '
        parameters.update({
            'q': 'filter:links %s' % (users_string),
        })
        url = config.TWITTER_SEARCH_URL
    twitter_response = requests.get(url, params=parameters, auth=auth)

    # Grr. Response is different if from search
    if config.TWITTER_USERS:
        statuses_with_links = [
            status for status in twitter_response.json()['statuses'] if status['entities'] and status['entities']['urls']
        ]
    else:
        statuses_with_links = [
            status for status in twitter_response.json() if status['entities'] and status['entities']['urls']
        ]

    # This algorithm could probably be better for determining relevance
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

    link_objects_to_export = []
    links = []
    for status in sorted_statuses:

        link = status['entities']['urls'][0]['expanded_url']
        # If we've already seen it, don't add it again
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
                if not link_title:
                    link_title = link
            except AttributeError:
                link_title = link
            link_title = "%s%s" % (link_title[0:100], '...')
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
    template_loader = jinja2.FileSystemLoader('../templates/')
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template('index.html')
    template_vars = {
        "links": link_objects,
        "stylesheet_name": settings.STYLESHEET_NAME
    }

    yesterday = get_yesterday()
    if os.path.isfile("%s/%s.html" % (
        config.OUTPUT_PATH,
        yesterday,
    )):
        template_vars['previous'] = yesterday

    index_html_path = "%s/index.html" % (config.OUTPUT_PATH)
    with open(index_html_path, 'w') as html:
        html.write(template.render(template_vars).encode('utf-8'))


if __name__ == "__main__":
    render_link_page(get_sorted_status_links())
