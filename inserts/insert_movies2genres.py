import json
from postgres import Postgres


class InsertData(object):

    def __init__(self, server, port, database, username, password):
        self.pg = Postgres(server, port, database, username, password)
        self.source_topic = 'movies'
        self.destination_topic = 'movies2genres'

    def insert(self, data):
        """
        This inserts the relevant json information
        into the table kino.movies.
        :param data: json data holding information on films.
        """

        genre_data = data['tmdb_genres']

        # We have to specify the tstamp, as the default value specificed in Django
        # only populates when called from Django.
        sql = """insert into movies_movies2genres (imdb_id, genre, tstamp)
                 select imdb_id
                      , name
                      , CURRENT_DATE
                   from json_to_recordset(%s) x (imdb_id varchar(1000), name varchar(1000))
                  where (imdb_id, name) not in (select imdb_id
                                                     , genre
                                                  from movie_movies2genres )"""

        self.pg.pg_cur.execute(sql, (json.dumps(genre_data), ))
        self.pg.pg_conn.commit()

