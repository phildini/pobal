#!/bin/bash

DATE=`date -d "yesterday" +%Y-%m-%d`
cp $TWEET_HTML_PATH/index.html $TWEET_HTML_PATH/$DATE.html
bash generate_html.sh