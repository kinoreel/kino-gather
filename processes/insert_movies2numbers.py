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
        self.destination_topic = 'movies2numbers'

    def run(self, data):
        """
        This inserts the relevant json information
        into the table kino.movies.
        :param data: json data holding information on films.
        """

        movie_data = data['tmdb_main']

        # We have to specify the tstamp, as the default value is only populated
        # when the insert is done via Django.
        sql = """insert into kino.movies2numbers (imdb_id, type, value, tstamp)
                 with pivoted_data as (
                 select imdb_id
                      , unnest(array['revenue', 'budget']) as type
                      , unnest(array[revenue, budget]) as value
                   from json_to_recordset( %s) x (imdb_id varchar(1000), revenue int, budget int)
                 )
                 select imdb_id
                      , type
                      , value
                      , CURRENT_DATE
                   from pivoted_data
                  where ( imdb_id, type ) not in (select imdb_id
                                                       , type
                                                    from kino.movies2numbers)"""

        self.pg.pg_cur.execute(sql, (json.dumps(movie_data), ))
        self.pg.pg_conn.commit()

