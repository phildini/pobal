#!/bin/bash

DATE=`TZ=America/Los_Angeles date -d "yesterday 13:00" +%Y-%m-%d`
cp -a $TWEET_HTML_PATH/index.html $TWEET_HTML_PATH/$DATE.html
bash /home/phildini/pobal/generate_html.sh