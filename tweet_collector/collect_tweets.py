# Install any required libraries
#!pip install tweepy
#!pip install kafka
#!pip install configparser

import time, datetime, ConfigParser, os, sys
sys.path.append('tweet_collector')
import twitterconnection as twitter

# Read config file that contains database and twitter connection info
config = ConfigParser.ConfigParser()
config.read('tweet_collector/config.ini')

# Connect to twitter and track stocks
twitter_con = twitter.TwitterConnection(config)

while True:
  try:
    twitter_con.search()
  except Exception as e:
    print(str(e))
  
#    print('Listening for tweets...')
#    twitter_con.track()
#
#    # Keep connection open for 5 minutes
#    time.sleep(600)