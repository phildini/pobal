#!/bin/bash

echo "Job Starting"
. .bash_profile
cd /home/phildini/pobal/
rm tweets.json
virtualenv .
. bin/activate
pip install -r requirements.txt
python fetch_links.py
cp styles.css $TWEET_HTML_PATH
echo "Job ending"