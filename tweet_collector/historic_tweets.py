# Install any required libraries
!pip install tweepy
!pip install kafka

import time, datetime, ConfigParser, os, sys
sys.path.append('tweet_collector')
import twitterconnection as twitter

config_file = 'tweet_collector/' + os.environ['config_file']

# Read config file that contains database and twitter connection info
config = ConfigParser.ConfigParser()
config.read(config_file)

# Connect to twitter and track stocks
twitter_con = twitter.TwitterConnection(config)

# Run search for historic tweets
try:
  twitter_con.search()
except Exception as e:
  print(str(e))