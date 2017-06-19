create or replace view gather.v_movies2keywords as
select x.imdb_id
     , name as keyword
  from gather.tmdb_keywords x
  left join kino.movies2keywords y
    on y.imdb_id = x.imdb_id
   and x.name = y.keyword
 where y.imdb_id is null;