create or replace view gather.v_companies as
select y.name
  from gather.tmdb_companies y
  left join kino.companies x
    on y.name = x.name
 where x.name is null