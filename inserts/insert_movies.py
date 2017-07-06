import json

from apis import GLOBALS
from py.postgres import Postgres


class InsertData(object):

    def __init__(self, server, port, database, username, password):
        self.pg = Postgres(server, port, database, username, password)
        self.source_topic = 'guidebox'
        self.destination_topic = 'movies'

    def insert(self, data):
        """
        This inserts the relevant json information
        into the table kino.movies.
        :param data: json data holding information on films.
        """
        omdb_movie_data = data['omdb_main']
        tmdb_movie_data = data['tmdb_main']

        sql = """insert into movies_movie (imdb_id, title, runtime, rated, released, orig_language)
                 select x.imdb_id
                      , x.title
                      , y.runtime
                      , x.rated
                      , y.release_date
                      , y.original_language
                   from json_to_recordset(%s) x (imdb_id varchar(1000), title varchar(100), rated varchar(1000))
                   join json_to_recordset(%s) y (imdb_id varchar(1000), runtime varchar(1000), release_date varchar(1000), original_language varchar(1000))
                     on x.imdb_id = y.imdb_id
                  where x.imdb_id not in (select imdb_id
                                            from kino.movies )"""

        self.pg.pg_cur.execute(sql, (json.dumps(omdb_movie_data), json.dumps(tmdb_movie_data)))
        self.pg.pg_conn.commit()

        return data



