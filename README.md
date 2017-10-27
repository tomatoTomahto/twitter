# Twitter Collection
This project allows you to collect and process historic tweets (up to 7 days in the past) or track real-time tweets from Twitter. 
All code is written in Python, and uses the [tweepy](http://tweepy.readthedocs.io/en/v3.5.0/) library, which provides 
a Python interface to Twitter's REST API available for developers. 

Twitter's REST API allows developers to pull a ton of information about tweets and the users that tweet them, including: 
* Tweet text
* Creation time
* Location
* Hashtags
* User Mentions
* Links
* Media (images, videos, etc)
* User name, description, location
* And more, see [Twitter Developer](https://developer.twitter.com) for more info

# Instructions
## Pre-Requisites
The code was built on Cloudera's Data Science Workbench, and the instructions below are written for deploying this project
on that tool. However all the code is written in Python and can be run in any Python environment.
* Cloudera Data Science Workbench (optional)
* Python 2.7 with the following libraries
  * tweepy
  * kafka
* Twitter API Key (get it from https://apps.twitter.com/ after creating a new Twitter Application)
  * access_token
  * access_token_secret
  * consumer_key
  * consumer_secret
  
There are 3 components to this project:
* Historic Tweet Collection
* Real-time Streaming Tweet Collection
* Real-time Tweet Processing
* Advanced Analytics on Historical Tweets

## Historic Data Collection
This application tracks a set of pre-specified search terms, which could be hashtags, usernames, or just general terms. Twitter
allows developers to [search](https://developer.twitter.com/en/docs/tweets/search/overview) for all tweets that match a query 
within the last 7 days for free. The instructions below outline how to use this application: 
1. Put your search terms into track.txt. Twitter has a Rate Limit of about 200 search terms per query. 
2. Edit config_example.ini with your Twitter API credentials and the output file to dump the tweets to. Optionally if your track.txt file has more than 200 terms, you can specify an offset line number to start from. The script will search the next 200 terms from that offset. Rename file to config.ini.
3. Run the Python script to search for your tweets: ```python tweet_collector/historic_tweets.py```

The script will write tweets to the specified output file in JSON format. Twitter also imposes rate limits on the number of requests
that can be made in a 15 minute interval. The script will automatically detect these limits and sleep for 15 minutes when they are 
hit. The tweets can then be analyzed further as described in the Analytics sections. 

## Real-time Streaming Tweet Collection
Similar to historic data collection, this application will track all tweets that have a specified search term in them. However, this
application uses Twitter's [Streaming API](https://developer.twitter.com/en/docs/tweets/filter-realtime/overview). The stream of tweets
can then be sent to Kafka to be consumed by a real-time processing framework, or simply written to a JSON file. Instructions below:
1. Put your search terms into track.txt
2. Edit config_example.ini with your Twitter API credentials. If you want to write the Tweet stream to Kafka, change output->type to kafka and edit the Kafka configuration. Rename file to config.ini.
3. Run the Python script to track tweets in real-time: ```python tweet_collector/streaming_tweets.py```

Similar to historic collection, Twitter imposes rate limits on the amount of data that can be streamed every 5 minutes, so the 
script will detect these limits and sleep for an appropriate amount of time before streaming new records. This script will run
continuously until stopped. 

## Real-time Tweet Processing
To do - Kafka->Streamsets job

## Advanced Analytics on Historical Tweets
To do - Spark analysis of historical twitter data