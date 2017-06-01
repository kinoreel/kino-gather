create table gather.tmdb_release_dates
  ( imdb_id varchar(100)
  , certification varchar(100)
  , iso_639_1 varchar(100)
  , note varchar(100)
  , release_date varchar(100)
  , type varchar(100)
   , tstamp date not null default CURRENT_DATE   
 );

