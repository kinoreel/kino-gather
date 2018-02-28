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
        self.destination_topic = 'movies2keywords'

    def run(self, data):
        """
        This inserts the relevant json information
        into the table kino.movies.
        :param data: json data holding information on films.
        """

        keyword_data = data['tmdb_keywords']
        # We have to specify the tstamp, as the default value is only populated
        # when the insert is done via Django.
        sql = """insert into kino.movies2keywords (imdb_id, keyword, tstamp)
                 select imdb_id
                      , lower(keyword)
                      , CURRENT_DATE
                   from json_to_recordset(%s) x (imdb_id varchar(1000), keyword varchar(100))
                     on conflict on constraint movies2keywords_pkey
                     do nothing"""
        self.pg.pg_cur.execute(sql, (json.dumps(keyword_data), ))
        self.pg.pg_conn.commit()
