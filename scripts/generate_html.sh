#!/bin/bash

echo "Job Starting"
. .bash_profile
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