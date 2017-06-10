create or replace function update_kino_tables() returns void as
$body$
declare

   l_cols varchar(4000);

   view2tables cursor for
     select *
        from gather.views2kino_tables
        order by insert_order asc;

begin

   for xx in view2tables loop

      select string_agg(a.attname,',')
       into l_cols
       from pg_attribute a
       join pg_class t on a.attrelid = t.oid
       join pg_namespace s on t.relnamespace = s.oid
      where a.attnum > 0
        and not a.attisdropped
        and t.relname = xx.view_name
        and s.nspname = 'gather';

      execute  'insert into kino.' || quote_ident(xx.kino_table) || ' ( ' || l_cols || ')
                select ' ||  l_cols || '
                  from gather.' || quote_ident(xx.view_name);

   end loop;

end;
$body$
language plpgsql volatile;