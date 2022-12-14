# PROJECT ABOUT SCRAPING TWEETS ABOUT MOVIES, DOING SENTIMENT ANALYSIS AND COMPARE THEM TO IMDB MOVIE'S RATINGS



## README file til gruppeprosjekt i INFO319 Big Data: En sentimental analyse av movie-tweets fra twitter, sammenlignet med ratings fra imdb

 
- For å kjøre koden, trengs det access til V2 endpoint av twitter. 
- Eneste token man trenger å legge inn, er bearer token. Dette gjøres i "tweet_harvester.py", og den skal legges inn...
- Nødvendige pakker og moduler man trenger å laste ned er: afinn, PyMovieDb (brukes til å hente ratings fra imdb), PySpark, Kafka-Python


### Slik kjører du programmet: 
- Først må du starte HDFS og Yarn med: "start-all.sh" i sparkdriver. 
- Så starter du zookeeper på driver, worker 1 og worker 2. 
- Og til slutt start kafka server på alle nodene (driver, worker 1, worker 2 og worker 3)
- Lag topicsene: "tweets", "movie_names" og "ratings". 
- Først må tweet_harvester kjøres, så imdb_ratings filen, og så pipeline. Dette gjøres i 3 forskjellige terminaler.
- For å stoppe: stoppe zookeeper på driver, worker 1 og 2: zkServer.sh stop ${ZOOKEEPER_HOME}/conf/zookeeper.properties
- Så kan alt stoppes ved å skrive i driveren: "stop-all.sh"



## Her forteller vi hva systemet kan brukes til med et spesifikt eksempel, og i tillegg kildene vi har brukt til prosjektet vårt. 
- Som output, har vi lagt inn query for to forskjellige dataframes. De har navnene "output1" og "output2"./
  Som default er output1 skrudd på og output2 skrudd av: 
  output1 gir den joinede dataframen med kolonnene "id", "tweet_text", "movie_name", "afinn_score" og "imdb_rating".
  output2 gir dataframe med "movie_name" og aggregert average afinn_score basert på movienames. 
  Vi greide ikke å få inn imdb_ratingene i samme dataframe som average afinn_score, men viser i query1 hvordan vi greide å bruke det der.

