create table gather.omdb_ratings
  ( imdb_id varchar(10) not null
  , source varchar(4000) not null
  , value varchar(100) not null
  , tstamp date not null default CURRENT_DATE
  , PRIMARY KEY (imdb_id, source)
  , FOREIGN KEY (imdb_id) references gather.kino_movies(imdb_id)
  )