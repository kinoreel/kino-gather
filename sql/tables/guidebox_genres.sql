create table gather.guidebox_genres
  ( imdb_id  varchar(10)
  , genre  varchar(100)
  , tstamp date not null default CURRENT_DATE
  , PRIMARY KEY (imdb_id, genre)
  , FOREIGN KEY (imdb_id) references gather.kino_movies(imdb_id)
  );
