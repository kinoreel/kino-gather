create table gather.tmdb_similar
   ( imdb_id varchar(100) not null
   , id varchar(100) not null
   , title varchar(100) not null
   , overview varchar(4000)
   , release_date varchar(100)
   , poster_path varchar(100)
   , original_language varchar(100)
   , original_title varchar(100)
   , genre_ids varchar(100)
   , popularity varchar(100)
   , vote_average varchar(100)
   , vote_count  varchar(100)
   , adult  varchar(100)
   , video varchar(100)
   , backdrop_path varchar(100)
   , tstamp date not null default CURRENT_DATE
   );