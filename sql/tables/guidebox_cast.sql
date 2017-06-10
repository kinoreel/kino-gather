create table gather.guidebox_cast
  ( imdb_id varchar(10)
  , person_imdb_id varchar(100)
  , name varchar(100)
  , primary key (person_imdb_id, imdb_id)
  );

