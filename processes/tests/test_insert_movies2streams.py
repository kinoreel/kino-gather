import unittest
import os
import json

from processes.insert_movies2streams import Main
from processes.postgres import Postgres

try:
    DB_SERVER = os.environ['DB_SERVER']
    DB_PORT = os.environ['DB_PORT']
    DB_DATABASE = os.environ['DB_DATABASE']
    DB_USER = os.environ['DB_USER']
    DB_PASSWORD = os.environ['DB_PASSWORD']
except KeyError:
    try:
        from processes.GLOBALS import DB_SERVER, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD
    except ImportError:
        print("No parameters provided")
        exit()


class TestInsertMovies2Streams(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.main = Main()
        cls.pg = Postgres(DB_SERVER, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD)
        # We insert the corresponding film into kino.movies
        sql = """insert into kino.movies (imdb_id, title, runtime, rated, released, orig_language, plot)
                 values ( 'tt2562232', 'Birdman or (The Unexpected Virtue of Ignorance)', 119, 'R'
                        , '2014-08-27', 'en', 'Some plot')"""
        cls.pg.pg_cur.execute(sql)
        cls.pg.pg_conn.commit()

    def setUp(self):
        with open('test_data.json') as data_file:
            self.data = json.load(data_file)
        self.pg.pg_cur.execute('delete from kino.movies2streams')
        self.pg.pg_conn.commit()

    def test_insert_movies(self):
        self.main.run(self.data)
        self.pg.pg_cur.execute('select imdb_id, source, url, currency, price, format, purchase_type '
                               '  from kino.movies2streams')
        result = self.pg.pg_cur.fetchall()
        expected_result = [('tt2562232', 'GooglePlay', 'https://play.google.com/store/movies/details?id=0MhS4b_yjuo',
                            '£', 2.49, 'hd', 'rental'),
                           ('tt2562232', 'iTunes', 'https://itunes.apple.com/gb/movie/birdman/id928608985',
                            '£', 3.49, 'sd', 'rental'),
                           ('tt2562232', 'iTunes', 'https://itunes.apple.com/gb/movie/birdman/id928608985',
                            '£', 3.49, 'hd', 'rental'),
                           ('tt2562232', 'iTunes', 'https://itunes.apple.com/gb/movie/birdman/id928608985',
                            '£', 4.99, 'hd', 'purchase'),
                           ('tt2562232', 'iTunes', 'https://itunes.apple.com/gb/movie/birdman/id928608985',
                            '£', 4.99, 'sd', 'purchase'),
                           ('tt2562232', 'YouTube', 'https://www.youtube.com/watch?v=0MhS4b_yjuo',
                            '£', 2.49, 'hd', 'rental')]
        self.assertEqual(set(result), set(expected_result))

    def test_insert_movies_no_itunes(self):
        sql = """
                insert into kino.movies2streams (imdb_id, source, url, format, purchase_type)
                values ('tt2562232', 'iTunes', 'https://itunes.apple.com/gb/movie/birdman/id928608985', 'hd', 'rental')
                """
        self.pg.pg_cur.execute(sql)
        self.pg.pg_conn.commit()

        self.data['itunes_main'] = []
        self.main.run(self.data)
        self.pg.pg_cur.execute('select imdb_id, source, url, currency, price, format, purchase_type '
                               '  from kino.movies2streams')
        result = self.pg.pg_cur.fetchall()
        expected_result = [('tt2562232', 'GooglePlay', 'https://play.google.com/store/movies/details?id=0MhS4b_yjuo',
                            '£', 2.49, 'hd', 'rental'),
                           ('tt2562232', 'YouTube', 'https://www.youtube.com/watch?v=0MhS4b_yjuo',
                            '£', 2.49, 'hd', 'rental')]
        self.assertEqual(set(result), set(expected_result))

    def test_insert_movies_no_youtube(self):
        # We insert some YouTube data and GooglePlay data, to check that it is removed from the table
        sql = """
            insert into kino.movies2streams (imdb_id, source, url, format, purchase_type)
            values ('tt2562232', 'YouTube', 'https://www.youtube.com/watch?v=0MhS4b_yjuo', 'hd', 'rental')
            """
        self.pg.pg_cur.execute(sql)
        sql = """
            insert into kino.movies2streams (imdb_id, source, url, format, purchase_type)
            values ('tt2562232', 'GooglePlay', 'https://play.google.com/store/movies/details?id=0MhS4b_yjuo',
                     'hd', 'rental')
            """
        self.pg.pg_cur.execute(sql)
        self.pg.pg_conn.commit()

        self.data['youtube_main'] = []
        self.main.run(self.data)
        self.pg.pg_cur.execute('select imdb_id, source, url, currency, price, format, purchase_type '
                               '  from kino.movies2streams')
        result = self.pg.pg_cur.fetchall()
        expected_result = [('tt2562232', 'iTunes', 'https://itunes.apple.com/gb/movie/birdman/id928608985', '£', 3.49,
                            'sd', 'rental'),
                           ('tt2562232', 'iTunes', 'https://itunes.apple.com/gb/movie/birdman/id928608985', '£', 3.49,
                            'hd', 'rental'),
                           ('tt2562232', 'iTunes', 'https://itunes.apple.com/gb/movie/birdman/id928608985', '£', 4.99,
                            'hd', 'purchase'),
                           ('tt2562232', 'iTunes', 'https://itunes.apple.com/gb/movie/birdman/id928608985', '£', 4.99,
                            'sd', 'purchase')]
        self.assertEqual(set(result), set(expected_result))

    @classmethod
    def tearDownClass(cls):
        cls.pg = Postgres(DB_SERVER, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD)
        cls.pg.pg_cur.execute('delete from kino.movies2streams')
        cls.pg.pg_cur.execute('delete from kino.movies')
        cls.pg.pg_conn.commit()

if __name__ == '__main__':
    unittest.main()
