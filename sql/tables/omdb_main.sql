create table gather.omdb_main
  ( imdbid varchar(10) not null
  , title varchar(250) not null
  , year varchar(10)
  , plot varchar(4000)
  , rated varchar(100)
  , country varchar(30)
  , language varchar(300)
  , runtime varchar(30)
  , type varchar(10)
  , released varchar(300)
  , poster varchar(4000)
  , production varchar(4000)
  , awards varchar(1000)
  , boxoffice varchar(1000)
  , website varchar(1000)
  , imdbvotes varchar(1000)
  , tstamp date not null default CURRENT_DATE
  , PRIMARY KEY (imdbid)
  , FOREIGN KEY (imdbid) references gather.kino_movies(imdb_id) 
  )