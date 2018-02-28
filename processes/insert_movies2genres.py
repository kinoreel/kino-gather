import json
import os

from processes.postgres import Postgres


try:
    DB_SERVER = os.environ['DB_SERVER']
    DB_PORT = os.environ['DB_PORT']
    DB_DATABASE = os.environ['DB_DATABASE']
    DB_USER = os.environ['DB_USER']
    DB_PASSWORD = os.environ['DB_PASSWORD']
except KeyError:
    try:
        from processes.GLOBALS import DB_SERVER, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD
    except ImportError:
        print("No parameters provided")
        exit()


class Main(object):

    def __init__(self):
        self.pg = Postgres(DB_SERVER, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD)
        self.source_topic = 'movies'
        self.destination_topic = 'movies2genres'

    def run(self, data):
        """
        This inserts the relevant json information
        into the table kino.movies.
        :param data: json data holding information on films.
        """
        genre_data = data['tmdb_genre']

        sql = """insert into kino.genres(genre)
                 select x.genre
                   from json_to_recordset(%s) x (genre varchar(1000))
                  where genre not in (select genre
                                       from kino.genres)
                  group by genre """

        self.pg.pg_cur.execute(sql, (json.dumps(genre_data), ))
        self.pg.pg_conn.commit()

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
        self.pg.pg_cur.execute(sql, (json.dumps(genre_data), ))
        self.pg.pg_conn.commit()
