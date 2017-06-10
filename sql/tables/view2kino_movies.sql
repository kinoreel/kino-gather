create table gather.views2kino_tables
   ( kino_table varchar(30) not null
   , view_name varchar(30) not null
   , insert_order integer
   , primary key (view_name)
   );