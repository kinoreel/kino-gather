create or replace view gather.v_movies as
select x.imdb_id
      , x.title
      , x.runtime
      , x.rated
      , x.released
    from gather.omdb_main x
    left join kino.movies y
    on x.imdb_id = y.imdb_id
    where y.imdb_id is null;