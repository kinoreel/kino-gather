create table gather.guidebox_sources
  ( imdb_id varchar(10)
  , source varchar(50)
  , link varchar(100)
  , display_name  varchar(100)
  , type  varchar(30)
  , tstamp date not null default CURRENT_DATE
  , PRIMARY KEY (imdb_id, source)
  , FOREIGN KEY (imdb_id) references gather.kino_movies(imdb_id)
  );