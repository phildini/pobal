#!/bin/bash

if [ "$(uname)" == "Darwin" ]; then
    DATE=`date -v -1d '+%Y-%m-%d'`
else
    DATE=`TZ=America/Los_Angeles date -d "yesterday 13:00" +%Y-%m-%d`
fi
echo $DATE
cp -a $TWEET_HTML_PATH/index.html $TWEET_HTML_PATH/$DATE.html
bash $POBAL_PATH/generate_html.sh