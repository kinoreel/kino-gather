create table gather.omdb_crew
  ( imdbid varchar(1000) not null
  , name varchar(100) not null
  , role varchar(100) not null
  , tstamp date not null default CURRENT_DATE
  , PRIMARY KEY (imdbid, name, role)
  , FOREIGN KEY (imdbid) references gather.kino_movies(imdb_id) 
  )
  