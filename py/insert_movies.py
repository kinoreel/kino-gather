import json
from postgres import Postgres
import GLOBALS

class InsertMovies(object):

    def __init__(self, server, port, database, username, password):
        self.pg = Postgres(server, port, database, username, password)


    def insert(self, data):
        '''
        This inserts the relevant json information
        into the table kino.movies.
        :param data: json data holding information on films.
        '''

        movie_data = data['omdb_main']

        sql = '''insert into kino.movies (imdb_id, title, runtime, rated, released)
                 select imdb_id
                      , title
                      , runtime
                      , rated
                      , released
                   from json_populate_recordset( NULL::kino.movies, %s)
                  where imdb_id not in (select imdb_id
                                          from  kino.movies )'''

        self.pg.pg_cur.execute(sql, (json.dumps(movie_data), ))
        self.pg.pg_conn.commit()

