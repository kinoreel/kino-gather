create or replace view gather.v_movies2persons as
select x.imdb_id
     , y.person_id
     , x.role
  from ( select imdb_id, name, 'Actor' as role
           from gather.tmdb_cast
          union all
         select imdb_id, name, job
           from gather.tmdb_crew ) x
  join kino.persons y
    on x.name = y.fullname
  left join kino.movies2persons z
    on z.imdb_id = x.imdb_id
   and z.person_id = y.person_id
 where z.imdb_id is null
 group by x.imdb_id, y.person_id, x.role
