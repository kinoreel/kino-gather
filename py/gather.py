import json

import GLOBALS

from get_omdb import GetOMDB
from get_tmdb import GetTMDB
from get_youtube import GetYoutube
from get_guidebox import GetGuidebox
from postgres import Postgres



class Gather(object):

    def __init__(self, db_conn):

        omdb_key = GLOBALS.OMDB_API
        youtube_films_api_key = GLOBALS.YOUTUBE_FILMS_API
        tmdb_api_key = GLOBALS.TMDB_API
        guidebox_api_key = GLOBALS.GUIDEBOX_API

        self.pg = Postgres(db_conn)
        self.omdb = GetOMDB(omdb_key)
        self.omdb.name = 'omdb'
        self.omdb.sql = 'select imdb_id ' \
                          'from gather.kino_movies ' \
                         'except ' \
                         'select imdb_id ' \
                           'from ( select imdb_id ' \
                                    'from gather.omdb_main ' \
                                   'union ' \
                                  'select imdb_id ' \
                                    'from gather.omdb_bad ' \
                                ') as tried_ids'

        self.tmdb = GetTMDB(tmdb_api_key)
        self.tmdb.name = 'tmdb'
        self.tmdb.sql = 'select imdb_id ' \
                          'from gather.kino_movies ' \
                         'except ' \
                         'select imdb_id ' \
                           'from ( select imdb_id ' \
                                    'from gather.tmdb_main ' \
                                   'union ' \
                                  'select imdb_id ' \
                                    'from gather.tmdb_bad ' \
                                ') as tried_ids'

        self.youtube_films = GetYoutube(youtube_films_api_key)
        self.youtube_films.name = 'youtube_films'
        self.youtube_films.sql = 'select ids_to_get.imdb_id, y.title ' \
                                  'from ( select imdb_id ' \
                                           'from gather.kino_movies ' \
                                         'except ' \
                                         'select imdb_id ' \
                                           'from ( select imdb_id ' \
                                                    'from gather.youtube_films_main ' \
                                                   'union ' \
                                                  'select imdb_id ' \
                                                    'from gather.youtube_films_bad ' \
                                                ') as tried_ids ' \
                                        ') as ids_to_get ' \
                                  'join gather.tmdb_main y ' \
                                    'on ids_to_get.imdb_id = y.imdb_id'

        self.guidebox = GetGuidebox(guidebox_api_key)
        self.guidebox.name = 'guidebox'
        self.guidebox.sql = 'select imdb_id ' \
                        'from gather.kino_movies ' \
                        'except ' \
                        'select imdb_id ' \
                        'from ( select imdb_id ' \
                        'from gather.guidebox_main ' \
                        'union ' \
                        'select imdb_id ' \
                        'from gather.guidebox_bad ' \
                        ') as tried_ids'


        self.apis = { 'omdb': self.omdb
                    , 'tmdb': self.tmdb
                    , 'youtube_films': self.youtube_films
                    , 'guidebox' : self.guidebox
                    }

    def get_imdb_ids(self, api):
        imdb_ids = self.pg.run_query(api.sql)
        return imdb_ids

    def get_movie_data(self, api, api_param):
        data = api.get_info(api_param)
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
        api_params = self.get_imdb_ids(api)
        c = 0
        for param in api_params:
            c +=1
            movie_info = self.get_movie_data(api, param)
            if movie_info:
                self.insert_data(movie_info)
            else:
                self.insert_bad_id(api, param[0])
            if divmod(c, 15) == 0:
                self.pg.pg_conn.commit()
        self.pg.pg_conn.commit()

    def insert_bad_id(self, api, imdb_id):
        sql = "insert into gather.{0} values (%s)".format(api.name+'_bad')
        self.pg.pg_cur.execute(sql, (imdb_id, ))

    def gather_new_kino_movies(self):
        for name, api in self.apis.items():
            self.update_gather_table(api)

    def gather_one_movie(self, imdb_id):
        movie_data = {}
        for name, api in self.apis.items():
            if name in ['tmdb', 'omdb', 'guidebox']:
                movie_data[name]= self.get_movie_data(api, (imdb_id,))
        return movie_data
