create or replace view v_person_roles as
select role
  from ( select role
           from gather.tmdb_cast
          union all
         select role
           from gather.tmdb_crew
       ) y
  left join kino.person_roles x
    on x.role = y.role
 where x.role is null