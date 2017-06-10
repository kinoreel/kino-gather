create or replace view gather.v_movies2ratings as
select x.imdb_id
     , lower(x.source) as source
     , to_number(value, '9')  as rating
  from gather.omdb_ratings x
  left join kino.movies2ratings y
    on y.imdb_id = x.imdb_id
 where y.imdb_id is null;
