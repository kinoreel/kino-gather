create table gather.omdb_ratings
  ( imdbid varchar(10) not null
  , source varchar(4000) not null
  , value varchar(100) not null
  , tstamp date not null default CURRENT_DATE
  , PRIMARY KEY (imdbid, source)
  , FOREIGN KEY (imdbid) references gather.kino_movies(imdb_id) 
  )