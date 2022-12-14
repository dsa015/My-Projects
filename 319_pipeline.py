from pyspark.sql import SparkSession
import json
from twitterpipe_globals import *
from pyspark.sql.functions import decode, get_json_object
from pyspark.sql.functions import udf
from pyspark.sql.types import DoubleType
from pyspark.sql.types import StructType, StructField, StringType
from pyspark.sql.functions import decode, from_json




# Spark tweet receiver ---------------------------------------------------------
spark = SparkSession.builder.appName('SparkTest').getOrCreate()
spark.sparkContext.setLogLevel('ERROR')

# incoming tweet stream
tweet_sdf = spark.readStream \
                .format('kafka') \
                .option('kafka.bootstrap.servers', KAFKA_SERVER) \
                .option('subscribe', TWEET_TOPIC) \
                .option('startingOffsets', 'earliest') \
                .load()

# keys in DataFrame from Kafka:
# |key|value|topic|partition|offset|timestamp|timestampType|

#this selects each tweet
selected_tweet_sdf = tweet_sdf \
                .select(decode(tweet_sdf.value, 'utf-8').alias('json_str')) \
                .select('*', get_json_object('json_str', '$.data.text').alias('text')) \
                .select("*", get_json_object("json_str", "$.data.author_id").alias("author_id")) \
                .select("*", get_json_object("json_str", "$.data.id").alias("id"))\
                .select("*", get_json_object("json_str", "$.Movie_Name").alias("Movie_Name"))\
                .select('id',"text",'Movie_Name')
                

#debug
#query = selected_tweet_sdf \
#        .writeStream \
#        .outputMode('update') \
#        .format("console") \
#        .start()
#query.awaitTermination()

# #Spark movie_name_sdf producer ---------------------------------------------------------
movie_name_sdf = selected_tweet_sdf \
                .select('id', 'Movie_Name') \
                .selectExpr('to_json(struct(*)) AS value')

#writestream to movie topic with each title and id
movie_name_sdf_writer = movie_name_sdf.writeStream \
                .format('kafka') \
                .option('kafka.bootstrap.servers', 'localhost:9092') \
                .option('topic', MOVIE_NAME_TOPIC) \
                .option('checkpointLocation', '.checkpoint2')\
                .start()


#debug
# query2 = movie_name_sdf \
#         .writeStream \
#         .outputMode('update') \
#         .format("console") \
#         .start()
#query2.awaitTermination()

# Sentiment analysis ---------------------------------------------------------
from afinn import Afinn
def afinn_score(text):
    af = Afinn()
    return af.score(text)

afinn_score_udf = udf(afinn_score)
spark.udf.register('afinn_score', afinn_score_udf)

text_schema = StructType([
             StructField('text', StringType(), False),
         ])

#sentiment score of each tweet
sentiment_sdf = selected_tweet_sdf \
                 .select('id', 'text', afinn_score_udf('text').alias('afinn_score'))

#debug
# query2 = sentiment_sdf \
#         .writeStream \
#         .outputMode('append') \
#         .format("console") \
#         .start()
# query2.awaitTermination()

# # Spark rating consumer ------------------------------------------------------------

#reads rating topic
rating_sdf = spark.readStream \
                .format('kafka') \
                .option('kafka.bootstrap.servers', "localhost:9092") \
                .option('subscribe', RATING_TOPIC) \
                .option('startingOffsets', 'earliest') \
                .load()

#selects id, title and rating 
selected_rating_sdf = rating_sdf \
                .select(decode(rating_sdf.value, 'utf-8').alias('json_str')) \
                .select('*', get_json_object('json_str', '$.id').alias('id')) \
                .select("*", get_json_object('json_str', '$.Movie_Name').alias("movie_name"))\
                .select("*", get_json_object('json_str', '$.imdb_rating').alias("imdb_rating"))\
                .select('id', 'movie_name', 'imdb_rating')

#debug
#query = selected_rating_sdf \
#        .writeStream \
#        .outputMode('update') \
#        .format("console") \
#        .start()
#query3.awaitTermination()



#Queries to turn on or off, two dataframe outputs

# Shows whole dataframe with each tweets afinn score 
joined_sdf = sentiment_sdf.join(selected_rating_sdf, 'id', 'inner')

#Shows average afinn score to each movie
sentiment_sdf2 = selected_tweet_sdf\
                .select('id', 'text', "Movie_Name",  afinn_score_udf('text').alias('afinn_score'), current_timestamp().alias("timestamp"))\
                .withWatermark("timestamp", "10 minutes")

grouped_df = sentiment_sdf2.withWatermark("timestamp", watermark)\
                .groupBy("Movie_Name", window("timestamp", watermark))\
                .agg(avg("afinn_score"))

avg_df = grouped_df.withColumnRenamed("avg(afinn_score)", "avg_score")




#output for joined sdf
ouput1 = joined_sdf \
        .writeStream \
        .outputMode('append') \
        .format("console") \
        .start()
output1.awaitTermination()

#output, can turn off the other output and then turn this on
#output2 = avg_df \
#        .writeStream \
#        .outputMode('update') \
#        .format("console") \
#        .start()
#output2.awaitTermination()

 



