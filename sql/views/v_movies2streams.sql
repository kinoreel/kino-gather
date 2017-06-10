create or replace view gather.v_movies2streams as
select x.imdb_id
	 , x.display_name as source
     , x.link
     , case when y.price is not null then '£' end as currency
     , to_number(y.price, '99.9') as price
     , y.format
     , y.type as purchase_type
  from gather.guidebox_sources x
  left join gather.guidebox_prices y
    on x.imdb_id = y.imdb_id
   and x.source = y.source
  left join kino.movies2streams z
    on x.imdb_id = z.imdb_id
 where z.imdb_id is null;