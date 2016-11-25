import tweepy
from tweepy.streaming import StreamListener
import json
import time
import traceback

class TwitterConnection():
    class MyListener(StreamListener):
        def __init__(self, tweets_to_insert):
            # Arrays of tweets - updated as tweets come in
            self._tweets_to_insert = tweets_to_insert

        # on_data() - called whenever a tweet is matched to our search terms
        def on_data(self, data):
            try:
                # Twitter returns data in JSON format - we need to decode it first
                tweet_json = json.loads(data)
                #print(tweet_json)

                # Check if twitter limit is exceeded
                if 'limit' in tweet_json:
                    print('Warning: tweet rate limit exceeded')
                    return True

                self._tweets_to_insert.append(tweet_json)
                return True
            except Exception as e:
                print('Error: ' + str(e))
                traceback.print_exc()
                return True

        # on_error - called when an error occurs
        def on_error(self, status):
            if status == 420:
                print(" Warning: twitter rate limit reached, sleeping for 1 minute")
                time.sleep(60)
            else:
                print("Error: " + str(status))
            return True

    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        # Store tweets temporarily and dump them to file at an interval
        self._tweets_to_insert = []

        # Store twitter API information
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        self._access_token = access_token
        self._access_token_secret = access_token_secret

        #This handles Twitter authetification and the connection to Twitter
        self._auth = tweepy.OAuthHandler(self._consumer_key, self._consumer_secret)
        self._auth.set_access_token(self._access_token, self._access_token_secret,)
        self._connect()

    # connect (PRIVATE) - connect to twitter via tweepy API using credentials
    def _connect(self):
        self._api = tweepy.API(self._auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        print('Connected to Twitter')

    # track - create a twitter listening to track a given set of search terms
    def track(self, track_terms):
        self._twitter_stream = tweepy.Stream(self._auth, self.MyListener(self._tweets_to_insert))
        self._twitter_stream.filter(track=track_terms, async=True)

    # disconnect - disconnect twitter stream
    def _disconnect(self):
        self._twitter_stream.disconnect()

    # commit_new_tweets - store all tweets and users captured over the last interval into our MySQL database
    def write_new_tweets(self, suffix):
        print('Writing tweets')
        self._twitter_stream.disconnect()
        time.sleep(30) # Wait until all tweets are in
        with open('tweets_' + suffix + '.json', 'w') as outfile:
            for tweet in self._tweets_to_insert:
                json.dump(tweet, outfile)
                outfile.write('\n')
            outfile.flush()
            outfile.close()
        self._tweets_to_insert = []
