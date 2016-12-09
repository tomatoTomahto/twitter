import twitterconnection as twitter
import time
import datetime
import configparser
import os

# Read config file that contains database and twitter connection info
if not os.path.isfile('config.ini'):
    print('Error: missing config.ini')
if not os.path.isfile('track.txt'):
    print('Error: missing track.txt')

config = configparser.ConfigParser()
config.read('config.ini')

# Connect to twitter and track stocks
twitter_con = twitter.TwitterConnection(config)

while True:
    print('Listening for tweets...')
    twitter_con.track()

    # Keep connection open for 5 minutes
    time.sleep(600)

    # Write all tweets to disk
    twitter_con.printStats()
