import json
from postgres import Postgres
import GLOBALS


class InsertData(object):

    def __init__(self, server, port, database, username, password):
        self.pg = Postgres(server, port, database, username, password)
        self.source_topic = 'movies'
        self.destination_topic = 'movies2numbers'

    def insert(self, data):
        """
        This inserts the relevant json information
        into the table kino.movies.
        :param data: json data holding information on films.
        """

        movie_data = data['tmdb_main']

        sql = """insert into kino.movies2numbers (imdb_id, type, value)
                 with pivoted_data as (
                 select imdb_id
                      , unnest(array['revenue', 'budget']) as type
                      , unnest(array[revenue, budget]) as value
                   from json_to_recordset( %s) x (imdb_id varchar(1000), revenue varchar(100), budget varchar(1000))
                 )
                 select imdb_id
                      , type
                      , cast(value as real)
                   from pivoted_data
                  where ( imdb_id, type ) not in (select imdb_id
                                                       , type
                                                    from kino.movies2numbers)"""

        self.pg.pg_cur.execute(sql, (json.dumps(movie_data), ))
        self.pg.pg_conn.commit()

