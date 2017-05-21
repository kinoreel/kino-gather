create table gather.tmdb_genres
   ( imdb_id varchar(100) not null
   , tmdb_id varchar(100) not null
   , genre_id varchar(100) not null
   , genre varchar(100) not null
   , tstamp date not null default CURRENT_DATE   
   );
