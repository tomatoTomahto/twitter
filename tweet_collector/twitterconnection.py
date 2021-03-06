import tweepy
from tweepy.streaming import StreamListener
import time, datetime, json, traceback
import kafkaconnection as kafka, filewriter

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
        self._access_token = config.get('twitter','access_token')
        self._access_token_secret = config.get('twitter','access_token_secret')
        self._consumer_key = config.get('twitter','consumer_key')
        self._consumer_secret = config.get('twitter','consumer_secret')

        # Retrieve terms to track
        track_file = open(config.get('track','file'), 'r')
        self._track_terms = [line.rstrip('\n').rstrip('\r') for line in track_file]
        self._start_index = int(config.get('track','offset'))

        # Store tweets temporarily and dump them to file at an interval
        self._tweets_to_insert = []

        # Initialize Kafka or File Writer
        if config.get('output','type') == 'kafka':
          self._writer = kafka.KafkaConnection(brokers=config.get('output','kafka_brokers'),
                                              topic=config.get('output','kafka_topic'))
        else:
          data_dir = 'data/'+datetime.datetime.now().strftime('%Y-%m-%d')+'-'
          self._writer = filewriter.FileWriter(filename=data_dir+config.get('output','filename'))

        #This handles Twitter authetification and the connection to Twitter
        self._auth = tweepy.OAuthHandler(self._consumer_key, self._consumer_secret)
        self._auth.set_access_token(self._access_token, self._access_token_secret,)
        self._connect()

        # Initialize twitter statistics
        self._twitter_stats = {'tweets':0}
        
        self._max_tweet_id = {}
        
        self._twitter_streams = []

    # connect (PRIVATE) - connect to twitter via tweepy API using credentials
    def _connect(self):
        self._api = tweepy.API(self._auth, wait_on_rate_limit=True, 
                               wait_on_rate_limit_notify=True,
                               parser=tweepy.parsers.ModelParser())

    # track - create a twitter listening to track a given set of search terms
    def track(self):
        track_terms = self._track_terms
        connections = -(-len(track_terms)/300)
        for connection in range(self._start_index,self._start_index+1):
          terms = track_terms[:300]
          twitter_stream = tweepy.Stream(self._auth, self.MyListener(writer=self._writer))
          twitter_stream.filter(track=terms, async=True)
          self._twitter_streams.append(twitter_stream)
          track_terms = track_terms[300:]
    
    def search(self):
      def limit_handled(cursor):
        while True:
          try:
            yield cursor.next()
          except tweepy.RateLimitError:
            print('Rate limit met, sleeping for 15 minutes')
            time.sleep(15 * 60)
      
      search_terms = self._track_terms
      searches = -(-len(search_terms)/10)
      for search in range(self._start_index, self._start_index+205):
        if search not in self._max_tweet_id.keys():
          self._max_tweet_id[search] = 0
          
        #print(len(search_terms[search*10:search*10+10]))
        query = ' OR '.join(search_terms[search*10:search*10+10])
        pageCnt = 0
        statuses = 0
        for page in limit_handled(tweepy.Cursor(self._api.search,
                                                q=query,
                                                count=100,
                                                since_id=self._max_tweet_id[search],
                                                result_type="recent",
                                                include_entities=True,
                                                lang="en").pages()):
          pageCnt += 1
          statusCnt = len(page)
          statuses += statusCnt
          #print('%d Statuses on Page %d for Search [%s]' % (statusCnt, pageCnt, query))
          for status in page:
            tweet_id = int(status._json['id'])
            #print(tweet_id)
            if tweet_id > self._max_tweet_id[search]:
              self._max_tweet_id[search] = tweet_id
            self._writer.write(json.dumps(status._json))
            
        print('Search: %d, Max Tweet ID: %d, Query: %s, Statuses: %d' % (search, self._max_tweet_id[search], query, statuses))

    # disconnect - disconnect twitter stream
    def _disconnect(self):
        for twitter_stream in self._twitter_streams:
          twitter_stream.disconnect()