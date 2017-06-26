create or replace view gather.v_person_roles as
select job as role
  from gather.tmdb_crew y
  left join kino.person_roles x
    on x.role = y.job
 where x.role is null
 group by job;