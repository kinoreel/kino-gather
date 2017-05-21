create table gather.tmdb_similar(
imdb_id varchar(100) not null,
page varchar(100),
results varchar(100),
total_pages varchar(100),
total_results varchar(100)
  , tstamp date not null default CURRENT_DATE   

);
