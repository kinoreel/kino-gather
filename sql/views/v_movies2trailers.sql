create or replace view gather.v_movies2trailers as
select x.imdb_id
     , 'https://www.youtube.com/watch?v=' || key as url
  from gather.tmdb_videos x
  left join kino.movies2genres y
    on y.imdb_id = x.imdb_id
 where y.imdb_id is null
   and type = 'Trailer'
   and site = 'YouTube';
