import json
import unittest

from apis import GLOBALS
from inserts.insert_movies2streams import InsertMovies2Streams
from py.postgres import Postgres

server = GLOBALS.PG_SERVER
port = GLOBALS.PG_PORT
db = GLOBALS.PG_DB_DEV
user = GLOBALS.PG_USERNAME
pw = GLOBALS.PG_PASSWORD

with open('test_data.json') as data_file:
    data = json.load(data_file)

class TestInsertMovies2Streams(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ins = InsertMovies2Streams(server, port, db, user, pw)
        cls.pg = Postgres(server, port, db, user, pw)
        # We insert the corresponding film into kino.movies
        # due to the foreign key constraint.
        sql = """insert into kino.movies (imdb_id, title, runtime, rated, released, orig_language)
                 values ('tt2562232', 'Birdman or (The Unexpected Virtue of Ignorance)', '119', 'R', '2014-08-27', 'en')"""
        cls.pg.pg_cur.execute(sql)
        cls.pg.pg_conn.commit()

    def test_insert_movies(self):
        self.ins.insert(data)
        self.pg.pg_cur.execute('select imdb_id, source, url, currency, price, format, purchase_type from kino.movies2streams')
        result = self.pg.pg_cur.fetchall()
        self.assertEqual(result, [('tt2562232', 'iTunes', 'https://itunes.apple.com/gb/movie/birdman/id928608985?uo=4&at=10laHb', '£', 7.9, 'HD', 'purchase'),
                                  ('tt2562232', 'iTunes', 'https://itunes.apple.com/gb/movie/birdman/id928608985?uo=4&at=10laHb', '£', 3.4, 'HD', 'rent'),
                                  ('tt2562232', 'iTunes', 'https://itunes.apple.com/gb/movie/birdman/id928608985?uo=4&at=10laHb', '£', 7.9, 'SD', 'purchase'),
                                  ('tt2562232', 'iTunes', 'https://itunes.apple.com/gb/movie/birdman/id928608985?uo=4&at=10laHb', '£', 2.4, 'SD', 'rent'),
                                  ('tt2562232', 'Google Play', 'https://play.google.com/store/movies/details?id=0MhS4b_yjuo', None, None, None, None),
                                  ('tt2562232', 'YouTube', 'https://www.youtube.com/watch?v=0MhS4b_yjuo', None, None, None, None)]
)


    @classmethod
    def tearDownClass(cls):
        cls.pg = Postgres(server, port, db, user, pw)
        cls.pg.pg_cur.execute('delete from kino.movies2streams')
        cls.pg.pg_cur.execute('delete from kino.movies')
        cls.pg.pg_conn.commit()

if __name__ == '__main__':
    unittest.main()