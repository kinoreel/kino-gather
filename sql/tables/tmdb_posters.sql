create table gather.tmdb_posters
  ( imdb_id varchar(100) not null
  , aspect_ratio varchar(100)
  , file_path varchar(100)
  , height varchar(100)
  , iso_code varchar(3)
  , vote_average varchar(100)
  , vote_count varchar(100)
  , width varchar(100)
  , tstamp date not null default CURRENT_DATE   
  );
