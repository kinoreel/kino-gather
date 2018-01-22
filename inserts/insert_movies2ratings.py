import json

try:
    from postgres import Postgres
except ImportError:
    from inserts.postgres import Postgres


class InsertData(object):

    def __init__(self, server, port, database, username, password):
        self.pg = Postgres(server, port, database, username, password)
        self.source_topic = 'movies'
        self.destination_topic = 'movies2ratings'

    def insert(self, data):
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
