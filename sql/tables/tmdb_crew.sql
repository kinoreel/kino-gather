create table gather.tmdb_crew
   ( imdb_id varchar(100) not null
   , id varchar(100) not null
   , name varchar(100) not null
   , job varchar(100) not null
   , department varchar(100) not null
   , credit_id varchar(100) not null
   , profile_path varchar(100)
   , tstamp date not null default CURRENT_DATE   
   , PRIMARY KEY (imdb_id, name, job)
   , FOREIGN KEY (imdb_id) references gather.kino_movies(imdb_id)
   );
