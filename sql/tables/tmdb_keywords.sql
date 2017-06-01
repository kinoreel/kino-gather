create table gather.tmdb_keywords
  ( imdb_id varchar(100) not null
  , id varchar(100)
  , name varchar(100)
   , tstamp date not null default CURRENT_DATE   
  );
