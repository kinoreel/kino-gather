create table gather.guidebox_trailers
  ( imdb_id varchar(10)
  , source varchar(30)
  , embed  varchar(100)
  , display_name  varchar(100)
  , link  varchar(100)
  , type  varchar(100)
  , tstamp date not null default CURRENT_DATE
  , PRIMARY KEY (imdb_id, source, link)
  , FOREIGN KEY (imdb_id) references gather.kino_movies(imdb_id)
  );