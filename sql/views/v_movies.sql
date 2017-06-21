create or replace view gather.v_movies as
select imdb_id
	  , title
      , runtime
      , rated
      , released
  from gather.omdb_main x
  left join kino.movies y
    on x.imdb_id = y.imdb_id
 where y.imdb_id is null;