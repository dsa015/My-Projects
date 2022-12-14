from PyMovieDb import IMDB
import json
import requests
import os

from kafka import KafkaConsumer, KafkaProducer

from twitterpipe_globals import *


class IMDBratings():

    def __init__(self):
        # connect to the kafka topics
        self.consumer = KafkaConsumer(
            MOVIE_NAME_TOPIC,
            bootstrap_servers=KAFKA_SERVER,
            client_id=f'media-harvester-{os.getpid()}',
            group_id='media-harvester-group',
            enable_auto_commit=False)
        self.producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)

    def start(self):   
        #for loop to get each movie title and add with rating
        for intel in self.consumer:
            value = intel.value.decode()
            json_obj = json.loads(value)
            tweet_id = json_obj["id"]
            movie_name = json_obj["Movie_Name"]
            imdb = IMDB()
            res = imdb.get_by_name(movie_name, tv=False)
            res2 = json.loads(res)

            try:
                imdb_rating = res2["rating"]["ratingValue"]
                json_obj = {
                    'id': tweet_id,
                    'Movie_Name': movie_name,
                    'imdb_rating': imdb_rating,
                }
            except KeyError:
                imdb_rating = "null"
                json_obj = {"id": tweet_id, "Movie_Name": movie_name, "imdb_rating": imdb_rating}
            json_data = json.dumps(json_obj).encode("utf-8")
            print('Sent:', json_data)
            self.producer.send(RATING_TOPIC, json_data)


            
    def stop(self):
        self.consumer.close()
        # self.producer.close()

imdb_ratings = IMDBratings()
imdb_ratings.start()

