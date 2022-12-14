from time import sleep

import tweepy
from kafka import KafkaProducer

from twitterpipe_globals import *
import json

NUM_TWEETS = 10  # how many tweets to harvest

class TweetHarvester():

    def __init__(self):
        # connect to the kafka topic
        self.producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
        # create the tweepy client and starts the sampling thread
        bearer_token = 'INPUT BEARER TOKEN IN HERE'
        self.streaming_client = tweepy.StreamingClient(bearer_token)
        self.num_tweets = NUM_TWEETS
        # start the incoming tweet stream
        self.streaming_client.on_data = self.on_data



    def start(self):
        self.tweet_count = 0
        try:
            #self.streaming_client.add_rules(tweepy.StreamRule("context:86.* lang:en -is:retweet"))
            self.streaming_client.filter(
                expansions = ['author_id'],
                user_fields = 'username',
                tweet_fields = ['author_id','id', 'text', 'created_at', 'context_annotations'],
                threaded=True)
        except KeyboardInterrupt:
            print('Stopping...')
            self.stop()

    def stop(self):
        self.on_finish()

    def on_data(self, json_data):
        """Tweepy calls this when it receives data from Twitter"""
        # pass on data
        data = json.loads(json_data.decode().strip())
        # this for loop goes throught the different keys within the tweet dict
        # in order to  find  each movie title name
        for k in data["data"]["context_annotations"]:
            for key, val in k.items():
                for x, y in val.items():
                    if y == "Movie":
                        movie_title = k.get("entity")["name"]
        data["Movie_Name"] = movie_title
        byte_data = json.dumps(data).encode("utf-8")
        self.producer.send(TWEET_TOPIC, byte_data) # json_data
        # keep count
        self.tweet_count += 1

        if self.tweet_count >= self.num_tweets:
            self.on_finish()
        #print(byte_data) to see the tweet that are sent to the pipeline

    def on_finish(self):
        self.streaming_client.disconnect()
        print('Stopping harvester...')
        sleep(10)
        print('Twitter harvester stopped!')

# start harvesting
tweet_harvester = TweetHarvester()
tweet_harvester.start()
