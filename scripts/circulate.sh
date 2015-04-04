#!/bin/bash

if [ "$(uname)" == "Darwin" ]; then
    DATE=`date -v -1d '+%Y-%m-%d'`
else
    DATE=`TZ=America/Los_Angeles date -d "yesterday 13:00" +%Y-%m-%d`
fi
echo $DATE
if [ -e $POBAL_HTML_PATH/$DATE.html ]; then
    echo "Previous day already copied"
else
    cp -a $POBAL_HTML_PATH/index.html $POBAL_HTML_PATH/$DATE.html
fi
bash $POBAL_PATH/scripts/generate_html.sh