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
if'twitter' not in config:
    print('Error: missing twitter config')
    exit()

tw_access_token = config['twitter']['access_token']
tw_access_token_secret = config['twitter']['access_token_secret']
tw_consumer_key = config['twitter']['consumer_key']
tw_consumer_secret = config['twitter']['consumer_secret']

# Retrieve terms to track
track_file = open('track.txt', 'r')
track_terms = [line.rstrip('\n') for line in track_file]
print('Tracking: ' + str(track_terms))

# Connect to twitter and track stocks
twitter_con = twitter.TwitterConnection(access_token=tw_access_token, access_token_secret=tw_access_token_secret,
                                        consumer_key=tw_consumer_key, consumer_secret=tw_consumer_secret)

while True:
    print('Listening for tweets...')
    twitter_con.track(track_terms=track_terms)

    # Keep connection open for 5 minutes
    time.sleep(600)

    # Write all tweets to disk
    twitter_con.write_new_tweets(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
