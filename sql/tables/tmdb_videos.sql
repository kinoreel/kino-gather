create table gather.tmdb_videos(
imdb_id varchar(100) not null,
id varchar(100),
iso_639_1 varchar(100),
iso_3166_1 varchar(100),
key varchar(100),
name varchar(100),
site varchar(100),
size varchar(100),
type varchar(100)
  , tstamp date not null default CURRENT_DATE   

);

create index tmdb_videos_imdb on gather.tmdb_videos(imdb_id);