create table gather.guidebox_cast
  ( imdb_id varchar(10)
  , person_imdb_id varchar(100)
  , name varchar(100)
  , tstamp date not null default CURRENT_DATE
  , PRIMARY KEY (imdb_id, name)
  , FOREIGN KEY (imdb_id) references gather.kino_movies(imdb_id)
  );

