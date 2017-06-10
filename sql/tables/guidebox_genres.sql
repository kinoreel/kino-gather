create table gather.guidebox_genres
  ( imdb_id  varchar(10)
  , genre  varchar(100)
  , tstamp date not null default CURRENT_DATE
  );
