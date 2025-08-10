import json

from processes.postgres import Postgres


def execute(data, pg: Postgres):
    """
    This inserts the relevant json information
    into the table kino.movies2genres.
    :param data: json data holding information on films.
    :param pg: Postgres connection object.
    """
    genre_data = data['tmdb_genre']

    sql = """insert into kino.genres(genre)
             select x.genre
               from json_to_recordset(%s) x (genre varchar(1000))
              where genre not in (select genre
                                   from kino.genres)
              group by genre """

    pg.pg_cur.execute(sql, (json.dumps(genre_data), ))
    pg.pg_conn.commit()

    # We have to specify the tstamp, as the default value specificed in Django
    # only populates when called from Django.
    sql = """insert into kino.movies2genres (imdb_id, genre, tstamp)
             select imdb_id
                  , genre
                  , CURRENT_DATE
               from json_to_recordset(%s) x (imdb_id varchar(1000), genre varchar(1000))
              where (imdb_id, genre) not in (select imdb_id
                                                 , genre
                                              from kino.movies2genres )"""
    pg.pg_cur.execute(sql, (json.dumps(genre_data), ))
    pg.pg_conn.commit()
