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
        self.destination_topic = 'movies2ratings'

    def run(self, data):
        """
        This inserts the relevant json information
        into the table kino.movies.
        :param data: json data holding information on films.
        """

        ratings_data = data['omdb_ratings']

        # We have to specify the tstamp, as the default value is only populated
        # when the insert is done via Django.
        sql = """insert into kino.movies2ratings (imdb_id, source, rating, tstamp)
                 select imdb_id
                      , lower(source) as source
                      , value
                      , CURRENT_DATE
                  from json_to_recordset(%s) x (imdb_id varchar(1000), source varchar(1000), value real)
                  where ( imdb_id, lower(source) ) not in (select imdb_id
                                                         , source
                                                      from kino.movies2ratings )"""

        self.pg.pg_cur.execute(sql, (json.dumps(ratings_data), ))
        self.pg.pg_conn.commit()
