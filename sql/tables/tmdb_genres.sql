create table gather.tmdb_genres
   ( imdb_id varchar(100) not null
   , id varchar(100) not null
   , name varchar(100) not null
   , tstamp date not null default CURRENT_DATE
   );
