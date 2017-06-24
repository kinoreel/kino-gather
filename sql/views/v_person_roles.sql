create or replace view v_person_roles as
select job
  from gather.tmdb_crew y
  left join kino.person_roles x
    on x.role = y.job
 where x.role is null