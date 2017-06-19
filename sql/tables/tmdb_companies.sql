create table gather.tmdb_companies
   ( imdb_id varchar(100) not null
   , id varchar(100) not null
   , name varchar(100) not null
   , tstamp date not null default CURRENT_DATE
   , PRIMARY KEY (imdb_id, name)
   , FOREIGN KEY (imdb_id) references gather.kino_movies(imdb_id)
   );