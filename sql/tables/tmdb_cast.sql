create table gather.tmdb_cast
   ( imdb_id varchar(100) not null
   , id varchar(100) not null
   , name varchar(100) not null
   , cast_id varchar(100) not null
   , character varchar(100) not null
   , credit_id varchar(100) not null
   , order_of_appearance varchar(100) not null
   , profile_path varchar(100)
   , tstamp date not null default CURRENT_DATE
   , PRIMARY KEY (imdb_id, name, character)
   , FOREIGN KEY (imdb_id) references gather.kino_movies(imdb_id)
   );

