#!/bin/bash

echo "Job Starting"
. .bash_profile

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

cd $POBAL_PATH
virtualenv .
. bin/activate
pip install -r requirements.txt
cd pobal
python fetch_links.py
if [ "$(uname)" == "Darwin" ]; then
    cp -R ../static/. $POBAL_HTML_PATH
else
    cp -a $POBAL_PATH/static/. $POBAL_HTML_PATH
fi
deactivate
echo "Job ending"