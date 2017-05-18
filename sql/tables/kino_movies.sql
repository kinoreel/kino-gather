create table gather.kino_movies 
   ( imdb_id varchar(10) not null
   , tstamp date not null default CURRENT_DATE
   , PRIMARY KEY (imdb_id)
   );