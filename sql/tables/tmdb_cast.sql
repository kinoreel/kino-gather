create table gather.tmdb_cast
   ( imdb_id varchar(100) not null
   , tmdb_id varchar(100) not null
   , person_id varchar(100) not null
   , person_name varchar(100) not null
   , character varchar(100) not null
   , order_of_appearance varchar(100) not null
  , tstamp date not null default CURRENT_DATE

   );
