create table gather.tmdb_main
   ( imdb_id varchar(100) not null
   , id varchar(100) not null
   , title varchar(100) not null
   , tagline varchar(1000)
   , overview varchar(4000)
   , runtime varchar(100)
   , revenue varchar(100)
   , budget varchar(100)
   , release_date varchar(100)
   , poster_path varchar(100)
   , original_language varchar(100)
   , original_title varchar(100)
   , status varchar(100)
   , popularity varchar(100)
   , vote_average varchar(100)
   , vote_count  varchar(100)
   , homepage varchar(100)
   , adult  varchar(100)
   , video varchar(1000)
   , backdrop_path varchar(100)
   , tstamp date not null default CURRENT_DATE
   );



