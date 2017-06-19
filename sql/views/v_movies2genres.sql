create or replace view gather.v_movies2genres as
select x.imdb_id
     , name as genre
  from gather.tmdb_genres x
  left join kino.movies2genres y
    on y.imdb_id = x.imdb_id
   and y.genre = x.name
 where y.imdb_id is null;
