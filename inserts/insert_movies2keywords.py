import json

from apis import GLOBALS
from py.postgres import Postgres


class InsertData(object):

    def __init__(self, server, port, database, username, password):
        self.pg = Postgres(server, port, database, username, password)
        self.source_topic = 'movies'
        self.destination_topic = 'movies2keywords'

    def insert(self, data):
        """
        This inserts the relevant json information
        into the table kino.movies.
        :param data: json data holding information on films.
        """

        keyword_data = data['tmdb_keywords']

        sql = """insert into kino.movies2keywords (imdb_id, keyword)
                 select imdb_id
                      , name
                   from json_to_recordset(%s) x (imdb_id varchar(1000), name varchar(100))
                  where ( imdb_id, name ) not in (select imdb_id
                                                       , keyword
                                                    from kino.movies2keywords )"""

        self.pg.pg_cur.execute(sql, (json.dumps(keyword_data), ))
        self.pg.pg_conn.commit()

