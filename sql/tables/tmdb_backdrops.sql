create table gather.tmdb_backdrops(
   , imdb_id varchar(100)
   , aspect_ratio varchar(100)
   , file_path varchar(100)
   , height varchar(100)
   , iso_639_1 varchar(100)
   , vote_average varchar(100)
   , vote_count varchar(100)
   , width varchar(100)
   , tstamp date not null default CURRENT_DATE
   , FOREIGN KEY (imdb_id) references gather.kino_movies(imdb_id)
);