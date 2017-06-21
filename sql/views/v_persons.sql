create or replace view gather.v_persons as
select name as fullname
  from ( select name
           from gather.tmdb_cast
          union all
         select name
           from gather.tmdb_crew ) x
 where name not in (select name
                         from kino.persons )