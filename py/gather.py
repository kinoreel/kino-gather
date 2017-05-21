import json

import GLOBALS

from get_omdb import GetOMDB
from get_tmdb import GetTMDB
from get_youtube import GetYoutube
from postgres import Postgres



class Gather(object):

    def __init__(self, db_conn):

        youtube_films_api_key = GLOBALS.YOUTUBE_FILMS_API
        tmdb_api_key = GLOBALS.TMDB_API

        self.pg = Postgres(db_conn)
        self.omdb = GetOMDB()
        self.omdb.bad_table = 'omdb_bad'
        self.omdb.sql = "select imdb_id " \
                        "  from gather.kino_movies " \
                        "except " \
                        "select imdbid " \
                        "  from gather.omdb_main"
        self.tmdb = GetTMDB(tmdb_api_key)
        self.tmdb.mbad_table = 'tmdb_bad'
        self.youtube_films = GetYoutube(youtube_films_api_key)
        self.youtube_films.main_table = 'youtube_films_main'


        self.apis = [ self.omdb
                    #, self.tmdb
                    #, self.youtube_films
                    ]

    def get_imdb_ids(self, api):
        imdb_ids = [e[0] for e in self.pg.run_query(api.sql)]
        return imdb_ids

    def get_movie_data(self, api, imdb_id):
        data = api.get_info(imdb_id)
        return data

    def insert_data(self, data):
        for table, rows in data.items():
            sql = "select string_agg(column_name, ', ' order by ordinal_position)" \
                  "  from information_schema.columns " \
                  " where table_name = %s" \
                  "   and column_name <> 'tstamp'"
            self.pg.pg_cur.execute(sql, (table,))
            cols = self.pg.pg_cur.fetchall()[0][0]
            self.pg.insert_json('gather', table, cols, rows)
        self.pg.pg_conn.commit()

    def update_gather_table(self, api):
        imdb_ids = self.get_imdb_ids(api)
        c = 0
        for id in imdb_ids:
            c +=1
            movie_info = self.get_movie_data(api, id)
            if movie_info:
                self.insert_data(movie_info)
            else:
                self.insert_bad_id(api, id)
            if divmod(c, 15) == 0:
                self.pg.commit()

    def insert_bad_id(self, api, imdb_id):
        sql = "insert into gather.{0} values (%s)".format(api.bad_table)
        self.pg.pg_cur.execute(sql, (imdb_id, ))

    def gather_new_kino_movies(self):
        for api in self.apis:
            self.update_gather_table(api)

    def gather_one_movie(self, imdb_id):
        movie_data = []
        for api in self.apis:
            movie_data.append(api.get_info(imdb_id))
        return movie_data


if __name__ =='__main__':
    with open('db_auth.json') as auth_file:
        auth = json.load(auth_file)['postgres_dev']
    get = Gather(auth)

