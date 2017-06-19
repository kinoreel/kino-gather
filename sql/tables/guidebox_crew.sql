create table gather.guidebox_crew
  ( imdb_id varchar(10)
  , person_imdb_id varchar(10)
  , name varchar(100)
  , job varchar(100)
  , tstamp date not null default CURRENT_DATE
  , PRIMARY KEY (imdb_id, name, job)
  , FOREIGN KEY (imdb_id) references gather.kino_movies(imdb_id)
  );
