create table gather.omdb_cast
  ( imdb_id varchar(1000) not null
  , name varchar(100) not null
  , role varchar(100) not null
  , tstamp date not null default CURRENT_DATE
  , PRIMARY KEY (imdb_id, name, role)
  , FOREIGN KEY (imdb_id) references gather.kino_movies(imdb_id)
  )
