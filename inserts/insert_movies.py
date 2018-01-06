import json

try:
    from postgres import Postgres
except ImportError:
    from inserts.postgres import Postgres


class InsertData(object):

    def __init__(self, server, port, database, username, password):
        self.pg = Postgres(server, port, database, username, password)
        self.source_topic = 'youtube'
        self.destination_topic = 'movies'

    def insert(self, data):
        """
        This inserts the relevant json information
        into the table kino.movies.
        :param data: json data holding information on films.
        """
        imdb_id = data['imdb_id']
        omdb_movie_data = data['omdb_main']
        tmdb_movie_data = data['tmdb_main']

        sql = """insert into kino.languages(language)
                 select x.original_language
                   from json_to_recordset(%s) x (original_language varchar(1000))
                  where original_language not in (select language
                                                    from kino.languages)
                  group by original_language """

        self.pg.pg_cur.execute(sql, (json.dumps(tmdb_movie_data),))
        self.pg.pg_conn.commit()

        # We attempt to delete our record from kino.movies first.
        # Due to foreign keys with 'on delete cascade', this clears all records from
        # the database associated with that imdb_id.

        sql = """delete from kino.movies
                  where imdb_id = '{0}'""".format(imdb_id)
        self.pg.pg_cur.execute(sql)
        self.pg.pg_conn.commit()

        sql = """insert into kino.movies (imdb_id, title, runtime, rated, released, orig_language, plot, tstamp)
                 select x.imdb_id
                      , y.title
                      , y.runtime
                      , x.rated
                      , y.release_date::date
                      , y.original_language
                      , y.plot
                      , CURRENT_DATE
                   from json_to_recordset(%s) x ( imdb_id varchar(15), rated varchar(10) )
                   join json_to_recordset(%s) y ( imdb_id varchar(15), title varchar(1000), runtime integer
                                                , release_date date, plot varchar(4000), original_language varchar(1000))
                     on x.imdb_id = y.imdb_id
              """
        self.pg.pg_cur.execute(sql, (json.dumps(omdb_movie_data), json.dumps(tmdb_movie_data)))
        self.pg.pg_conn.commit()

        return data



