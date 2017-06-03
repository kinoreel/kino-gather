create table gather.guidebox_bad
   ( imdb_id varchar(10) not null
   , tstamp date not null default CURRENT_DATE
   , PRIMARY KEY (imdb_id)
   );