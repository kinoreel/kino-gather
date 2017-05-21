import unittest
import json

from gather import Gather
from postgres import Postgres

with open('db_auth.json') as auth_file:
    auth = json.load(auth_file)['postgres_dev']

pg = Postgres(auth)
#TODO: Move to test folder
#TODO: Better test imdb_ids so we can better predict results.
class TestGatherOMDB(unittest.TestCase):

    def setUp(self):
        self.get = Gather(auth)
        pg.pg_cur.execute("delete from gather.omdb_bad")
        pg.pg_cur.execute("delete from gather.omdb_main")
        pg.pg_cur.execute("delete from gather.omdb_crew")
        pg.pg_cur.execute("delete from gather.omdb_cast")
        pg.pg_cur.execute("delete from gather.omdb_ratings")
        pg.pg_cur.execute("delete from gather.kino_movies")
        pg.pg_cur.execute("insert into gather.kino_movies values ('tt4285496')")
        pg.pg_cur.execute("insert into gather.kino_movies values ('tt2562232')")
        pg.pg_cur.execute("insert into gather.kino_movies values ('tt0245712')")
        pg.pg_conn.commit()
        self.omdb_tables = ['omdb_cast', 'omdb_crew', 'omdb_main', 'omdb_ratings']

    def tearDown(self):
        pg.pg_cur.execute("delete from gather.omdb_bad")
        pg.pg_cur.execute("delete from gather.omdb_main")
        pg.pg_cur.execute("delete from gather.omdb_crew")
        pg.pg_cur.execute("delete from gather.omdb_cast")
        pg.pg_cur.execute("delete from gather.omdb_ratings")
        pg.pg_cur.execute("delete from gather.kino_movies")
        pg.pg_conn.commit()

    def test_get_imdb_ids_omdb(self):
        omdb = self.get.apis[0]
        imdb_ids = self.get.get_imdb_ids(omdb)
        self.assertEqual(sorted(imdb_ids), [('tt0245712',), ('tt2562232',), ('tt4285496',)])

    def test_get_imdb_ids_omdb_with_bad(self):
        pg.pg_cur.execute("insert into gather.omdb_bad values ('tt0245712')")
        pg.pg_conn.commit()
        omdb = self.get.apis[0]
        imdb_ids = self.get.get_imdb_ids(omdb)
        self.assertEqual(sorted(imdb_ids), [('tt2562232',), ('tt4285496',)])
        pg.pg_cur.execute("delete from gather.omdb_bad where imdb_id = 'tt0245712'")
        pg.pg_conn.commit()

    def test_get_movie_data_omdb(self):
        omdb = self.get.apis[0]
        api_param = ('tt4285496',)
        data = self.get.get_movie_data(omdb, api_param)
        dict_keys = sorted(list(data.keys()))
        self.assertEqual(dict_keys, self.omdb_tables )
        for key in dict_keys:
            sql = "select column_name from information_schema.columns where table_name = %s and column_name <> 'tstamp'"
            pg.pg_cur.execute(sql, (key,))
            table_columns = [ e[0] for e in pg.pg_cur.fetchall() ]
            table_keys = [e.lower() for e in data[key][0].keys()]
            self.assertEqual(sorted(table_keys), sorted(table_columns))

    def test_insert_data_omdb(self):
        omdb = self.get.apis[0]
        api_param = ('tt4285496',)
        data = self.get.get_movie_data(omdb, api_param)
        self.get.insert_data(data)
        dict_keys = sorted(list(data.keys()))
        for key in dict_keys:
            sql = 'select count(*) from {0}.{1}'.format('gather', key)
            pg.pg_cur.execute(sql)
            table_count = pg.pg_cur.fetchall()[0][0]
            if key == 'omdb_main':
                self.assertEqual(table_count, 1)
            else:
                self.assertGreaterEqual(table_count, 1)
        pg.pg_cur.execute("delete from gather.omdb_main")
        pg.pg_cur.execute("delete from gather.omdb_crew")
        pg.pg_cur.execute("delete from gather.omdb_cast")
        pg.pg_cur.execute("delete from gather.omdb_ratings")
        pg.pg_cur.execute("delete from gather.omdb_bad")
        pg.pg_conn.commit()

    def test_update_gather_table_omdb(self):
        omdb = self.get.apis[0]
        self.get.update_gather_table(omdb)
        sql = 'select imdb_id from gather.omdb_bad'
        pg.pg_cur.execute(sql)
        imdb_ids = [e[0] for e in pg.pg_cur.fetchall()]
        self.assertEqual(imdb_ids, ['tt2562232'])
        for table_name in self.omdb_tables:
            sql = 'select imdbid from {0}.{1} group by imdbid'.format('gather', table_name)
            pg.pg_cur.execute(sql)
            imdb_ids = [e[0] for e in pg.pg_cur.fetchall()]
            self.assertEqual(sorted(imdb_ids),  ['tt0245712', 'tt4285496'])
            sql = 'delete from {0}.{1}'.format('gather', table_name)
            pg.pg_cur.execute(sql)

class TestGatherYoutubeFilms(unittest.TestCase):

    def setUp(self):
        self.get = Gather(auth)
        pg.pg_cur.execute("delete from gather.youtube_films_bad")
        pg.pg_cur.execute("delete from gather.youtube_films_main")
        pg.pg_cur.execute("delete from gather.youtube_films_other")
        pg.pg_cur.execute("delete from gather.omdb_main")
        pg.pg_cur.execute("delete from gather.kino_movies")
        pg.pg_cur.execute("insert into gather.kino_movies values ('tt4285496')")
        pg.pg_cur.execute("insert into gather.kino_movies values ('tt2562232')")
        pg.pg_cur.execute("insert into gather.kino_movies values ('tt0245712')")
        pg.pg_cur.execute("insert into gather.omdb_main (imdbid, title) values ('tt4285496', 'embrace of the serpent')")
        pg.pg_cur.execute("insert into gather.omdb_main (imdbid, title) values ('tt2562232', 'birdman or (the unexpected virtue of ignorance)')")
        pg.pg_cur.execute("insert into gather.omdb_main (imdbid, title) values ('tt0245712', 'amores perros')")
        pg.pg_conn.commit()
        self.youtube_films_tables = ['youtube_films_main', 'youtube_films_other']

    def tearDown(self):
        pg.pg_cur.execute("delete from gather.youtube_films_bad")
        pg.pg_cur.execute("delete from gather.youtube_films_main")
        pg.pg_cur.execute("delete from gather.youtube_films_other")
        pg.pg_cur.execute("delete from gather.omdb_main")
        pg.pg_cur.execute("delete from gather.kino_movies")
        pg.pg_conn.commit()

    def test_get_imdb_ids_youtube_films(self):
        you_films = self.get.apis[2]
        imdb_ids = self.get.get_imdb_ids(you_films)
        self.assertEqual(sorted(imdb_ids),[('tt0245712', 'amores perros'), ('tt2562232', 'birdman or (the unexpected virtue of ignorance)'), ('tt4285496', 'embrace of the serpent')])

    def test_get_imdb_ids_with_bad_youtube_films(self):
        pg.pg_cur.execute("insert into gather.youtube_films_bad values ('tt0245712')")
        pg.pg_conn.commit()
        you_films = self.get.apis[2]
        imdb_ids = self.get.get_imdb_ids(you_films)
        self.assertEqual(sorted(imdb_ids), [('tt2562232', 'birdman or (the unexpected virtue of ignorance)'), ('tt4285496', 'embrace of the serpent')])
        pg.pg_cur.execute("delete from gather.youtube_films_bad where imdb_id = 'tt0245712'")
        pg.pg_conn.commit()

    def test_get_movie_data_youtube_films(self):
        you_films = self.get.apis[2]
        api_param = ('tt4285496', 'embrace of the serpent')
        data = self.get.get_movie_data(you_films, api_param)
        dict_keys = sorted(list(data.keys()))
        self.assertEqual(dict_keys, self.youtube_films_tables )
        for key in dict_keys:
            sql = "select column_name from information_schema.columns where table_name = %s and column_name <> 'tstamp'"
            pg.pg_cur.execute(sql, (key,))
            table_columns = [ e[0] for e in pg.pg_cur.fetchall() ]
            table_keys = [e.lower() for e in data[key][0].keys()]
            self.assertEqual(sorted(table_keys), sorted(table_columns))

    def test_insert_data_youtube_films(self):
        you_films = self.get.apis[2]
        api_param = ('tt4285496', 'embrace of the serpent')
        data = self.get.get_movie_data(you_films, api_param)
        self.get.insert_data(data)
        dict_keys = sorted(list(data.keys()))
        for key in dict_keys:
            sql = 'select count(*) from {0}.{1}'.format('gather', key)
            pg.pg_cur.execute(sql)
            table_count = pg.pg_cur.fetchall()[0][0]
            if key == 'youtube_films_main':
                self.assertEqual(table_count, 1)
            else:
                self.assertGreaterEqual(table_count, 1)
        pg.pg_cur.execute("delete from gather.youtube_films_main")
        pg.pg_cur.execute("delete from gather.youtube_films_other")
        pg.pg_conn.commit()

    def test_update_gather_table_youtube_films(self):
        youtube_films = self.get.apis[2]
        self.get.update_gather_table(youtube_films)
        sql = 'select imdb_id from gather.youtube_films_bad'
        pg.pg_cur.execute(sql)
        imdb_ids = [e[0] for e in pg.pg_cur.fetchall()]
        self.assertEqual(imdb_ids, [])
        sql = 'select imdb_id from gather.youtube_films_main group by imdb_id'
        pg.pg_cur.execute(sql)
        imdb_ids = [e[0] for e in pg.pg_cur.fetchall()]
        self.assertEqual(sorted(imdb_ids),  ['tt0245712', 'tt2562232', 'tt4285496'])
        sql = 'delete from  gather.youtube_films_main'
        pg.pg_cur.execute(sql)
        sql = 'select imdb_id from gather.youtube_films_other group by imdb_id'
        pg.pg_cur.execute(sql)
        imdb_ids = [e[0] for e in pg.pg_cur.fetchall()]
        self.assertEqual(sorted(imdb_ids), ['tt0245712', 'tt4285496'])
        sql = 'delete from  gather.youtube_films_other'
        pg.pg_cur.execute(sql)


