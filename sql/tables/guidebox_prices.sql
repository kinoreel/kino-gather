create table gather.guidebox_prices
  ( imdb_id varchar(10)
  , price varchar(10)
  , pre_order varchar(10)
  , format varchar(10)
  , type varchar(100)
  , source varchar(100)
  , tstamp date not null default CURRENT_DATE
  , PRIMARY KEY (imdb_id, price, source, format)
  , FOREIGN KEY (imdb_id) references gather.kino_movies(imdb_id)
  );