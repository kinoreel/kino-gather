create or replace view gather.v_movies as
select imdb_id
	  , title
      , runtime
      , rated
      , released
  from gather.omdb_main
 where imdb_id not in ( select imdb_id
                          from kino.movies );