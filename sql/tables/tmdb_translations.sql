create table gather.tmdb_translations
   ( imdb_id varchar(100) not null
   , iso_639_1 varchar(100)
   , iso_3166_1 varchar(100)
   , name varchar(100)
   , english_name varchar(100)
   , tstamp date not null default CURRENT_DATE
   );
