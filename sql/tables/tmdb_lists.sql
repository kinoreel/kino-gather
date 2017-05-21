create table gather.tmdb_lists
  ( imdb_id varchar(100)
  , description varchar(100)
  , favorite_count varchar(100)
  , id varchar(100)
  , item_count varchar(100)
  , iso_639_1 varchar(100)
  , list_type varchar(100)
  , name varchar(100)
  , poster_path varchar(100)
   , tstamp date not null default CURRENT_DATE   
  );

