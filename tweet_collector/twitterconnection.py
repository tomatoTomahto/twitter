import tweepy
from tweepy.streaming import StreamListener
import time, datetime, json, traceback
import kafkaconnection as kafka

class TwitterConnection():
    class MyListener(StreamListener):
        def __init__(self, writer):
            # Arrays of tweets - updated as tweets come in
            self._writer = writer

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

                #self._tweets_to_insert.append(tweet_json)
                self._writer.write(data)
                #print(data)

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

    def __init__(self, config):
        if 'twitter' not in config:
            raise Exception('Error: missing [twitter] config')
        elif 'track' not in config:
            raise Exception('Error: missing [track] config')
        elif 'kafka' not in config:
            raise Exception('Error: missing [kafka] config')

        # Twitter credentials
        self._access_token = config['twitter']['access_token']
        self._access_token_secret = config['twitter']['access_token_secret']
        self._consumer_key = config['twitter']['consumer_key']
        self._consumer_secret = config['twitter']['consumer_secret']

        # Retrieve terms to track
        track_file = open(config['track']['file'], 'r')
        self._track_terms = [line.rstrip('\n') for line in track_file]

        # Store tweets temporarily and dump them to file at an interval
        self._tweets_to_insert = []

        # Initialize Kafka
        self._kafka = kafka.KafkaConnection(brokers=config['kafka']['brokers'],
                                            topic=config['kafka']['topic'])

        #This handles Twitter authetification and the connection to Twitter
        self._auth = tweepy.OAuthHandler(self._consumer_key, self._consumer_secret)
        self._auth.set_access_token(self._access_token, self._access_token_secret,)
        self._connect()

        # Initialize twitter statistics
        self._twitter_stats = {'tweets':0}

    # connect (PRIVATE) - connect to twitter via tweepy API using credentials
    def _connect(self):
        self._api = tweepy.API(self._auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        print('Connected to Twitter')

    # track - create a twitter listening to track a given set of search terms
    def track(self):
        self._twitter_stream = tweepy.Stream(self._auth, self.MyListener(writer=self._kafka))
        self._twitter_stream.filter(track=self._track_terms, async=True)

    # disconnect - disconnect twitter stream
    def _disconnect(self):
        self._twitter_stream.disconnect()

    def printStats(self):
        dt = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        print(dt + ':[' + ','.join([key+':'+str(value) for key,value in self._twitter_stats.items()]))

        for stat in self._twitter_stats.key():
            self._twitter_stats[stat] = 0