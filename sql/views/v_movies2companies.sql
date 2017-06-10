create or replace view gather.v_movies2companies as
select x.imdb_id
     , y.company_id
     , 'Production'::text as role
  from gather.tmdb_companies x
  join kino.companies y
    on x.name = y.name
  left join kino.movies2companies z
    on y.company_id = z.company_id
   and x.imdb_id = z.imdb_id
 where z.imdb_id is null
 group by x.imdb_id, y.company_id