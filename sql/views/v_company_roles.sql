create or replace view v_company_roles as
select 'Production'
  from gather.tmdb_companies y
  left join kino.company_roles x
    on x.role = y.role
 where x.role is null
 group by