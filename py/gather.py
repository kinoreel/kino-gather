import json

from get_omdb import GetOMDB
from get_tmdb import GetTMDB
from get_youtube import GetYoutube
from postgres import Postgres


class Gather(object):

    def __init__(self, db_conn):

        with open('api_keys.json') as keys_file:
            youtube_films_api_key = json.load(keys_file)['youtube_api']
            tmdb_api_key = json.load(keys_file)['tmdb_api']

        self.pg = Postgres(db_conn)
        self.omdb = GetOMDB()
        self.omdb.main_table = 'omdb_main'
        self.tmdb = GetTMDB(tmdb_api_key)
        self.tmdb.main_table = 'tmdb_main'
        self.youtube_films = GetYoutube(youtube_films_api_key)
        self.youtube_films.main_table = 'youtube_films_main'

        self.omdb.sql = "select imdb_id " \
                        "  from gather.kino_movies " \
                        "except " \
                        "select imdbid " \
                        "  from gather.omdb_main"

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

    def update_gather_table(self, api):
        imdb_ids = self.get_imdb_ids(api)
        c = 0
        for id in imdb_ids:
            c +=1
            movie_info = self.get_movie_data(api, id)
            self.insert_data(movie_info)
            if divmod(c, 15) == 0:
                self.pg.commit()

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

