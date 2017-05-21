create table gather.tmdb_companies
   ( imdb_id varchar(100) not null
   , tmdb_id varchar(100) not null
   , company_id varchar(100) not null
   , company_name varchar(100) not null
   , tstamp date not null default CURRENT_DATE

   );
