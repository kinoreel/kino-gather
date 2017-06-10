create table gather.guidebox_main
  ( imdb_id varchar(10)
  , id varchar(10)
  , rating varchar(10)
  , duration varchar(10)
  , overview text
  , title  varchar(400)
  , release_date  varchar(30)
  , wikipedia_id  varchar(20)
  , metacritic  varchar(100)
  , tstamp date not null default CURRENT_DATE
  , PRIMARY KEY (imdb_id)
  , FOREIGN KEY (imdb_id) references gather.kino_movies(imdb_id)
  );