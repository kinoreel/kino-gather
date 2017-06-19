create table gather.tmdb_alternative_titles
   ( imdb_id varchar(100) not null
   , iso_3166_1 varchar(3)
   , title varchar(100)
   , tstamp date not null default CURRENT_DATE
   , PRIMARY KEY (imdb_id, title)
   , FOREIGN KEY (imdb_id) references gather.kino_movies(imdb_id)
   );


