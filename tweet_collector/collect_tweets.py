# Install any required libraries
#!pip install tweepy
#!pip install kafka

import time, datetime, configparser, os, sys
sys.path.append('tweet_collector')
import twitterconnection as twitter

# Read config file that contains database and twitter connection info
config = configparser.ConfigParser()
config.read('tweet_collector/config.ini')

# Connect to twitter and track stocks
twitter_con = twitter.TwitterConnection(config)

while True:
    print('Listening for tweets...')
    twitter_con.track()

    # Keep connection open for 5 minutes
    time.sleep(600)

    # Write all tweets to disk
#    twitter_con.printStats()
