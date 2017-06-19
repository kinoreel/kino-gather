create or replace view gather.v_movies2numbers as
select x.imdb_id,
       unnest(array['revenue', 'budget']) AS type,
       unnest(array[revenue, budget]) AS value
  from gather.tmdb_main x
  left join kino.movies2numbers y
    on y.imdb_id = x.imdb_id
 where y.imdb_id is null;