create or replace view gather.v_movies2posters as
select x.imdb_id
     , max('http://image.tmdb.org/t/p/w185/' || x.file_path ) as url
 from gather.tmdb_posters x
 left join kino.movies2posters y
   on x.imdb_id = y.imdb_id
where y.imdb_id is null
group by x.imdb_id
