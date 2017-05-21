create table gather.tmdb_crew
   ( imdb_id varchar(100) not null
   , tmdb_id varchar(100) not null
   , person_id varchar(100) not null
   , person_name varchar(100) not null
   , department varchar(100) not null
   , job varchar(100) not null
   , tstamp date not null default CURRENT_DATE   
   );
