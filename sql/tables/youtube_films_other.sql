create table gather.youtube_films_other
    ( imdb_id varchar(10) not null
    , orig_title varchar(1000) not null
    , video_id varchar(30)
    , title varchar(1000)
    , description varchar(4000)
    , caption varchar(4000)
    , duration varchar(15)
    , region varchar(4000)
    , dimension varchar(30)
    , definition varchar(3)
    , published varchar(250)
    , licenced varchar(15)
    , channel_title varchar(250)
    , channel_id varchar(30)
    , comments varchar(10)
    , dislikes varchar(10)
    , likes varchar(10)
    , tstamp date default current_date
    , PRIMARY KEY (imdb_id, video_id)
    , FOREIGN KEY (imdb_id) references gather.kino_movies(imdb_id)
    );
