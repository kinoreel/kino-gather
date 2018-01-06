import json

try:
    from postgres import Postgres
except ImportError:
    from inserts.postgres import Postgres


class InsertData(object):

    def __init__(self, server, port, database, username, password):
        self.pg = Postgres(server, port, database, username, password)
        self.source_topic = 'movies'
        self.destination_topic = 'movies2trailers'

    def insert(self, data):
        """
        This inserts the relevant json information
        into the table kino.movies.
        :param data: json data holding information on films.
        """
        trailer_data = data['tmdb_trailer']

        sql = """insert into kino.movies2trailers (imdb_id, url, tstamp)
                 select imdb_id
                      , 'https://www.youtube.com/watch?v=' || url
                      , CURRENT_DATE
                   from json_to_recordset( %s) x (imdb_id varchar(1000), url varchar(100))
                     on conflict on constraint movies2trailers_pkey
                     do nothing"""

        self.pg.pg_cur.execute(sql, (json.dumps(trailer_data), ))
        self.pg.pg_conn.commit()