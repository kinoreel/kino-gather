create or replace view gather.v_company_roles as
select 'Production'::text as role
 where 'Production' not in (select role
                              from kino.company_roles)