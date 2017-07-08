import json

from apis import GLOBALS
from py.postgres import Postgres


class InsertData(object):

    def __init__(self, server, port, database, username, password):
        self.pg = Postgres(server, port, database, username, password)
        self.source_topic = 'movies'
        self.destination_topic = 'movies2posters'

    def insert(self, data):
        """
        This inserts the relevant json information
        into the table kino.movies.
        :param data: json data holding information on films.
        """

        movie_data = data['tmdb_main']

        sql = """insert into movies_movies2posters(imdb_id, url)
                 select imdb_id
                      , 'http://image.tmdb.org/t/p/w185/' || poster_path
                   from json_to_recordset( %s) x (imdb_id varchar(1000), poster_path varchar(100))
                  where ( imdb_id ) not in (select imdb_id
                                              from kino.movies2posters )"""

        self.pg.pg_cur.execute(sql, (json.dumps(movie_data), ))
        self.pg.pg_conn.commit()