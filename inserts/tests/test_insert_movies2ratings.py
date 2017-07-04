import json
import unittest

from apis import GLOBALS
from inserts.insert_movies2ratings import InsertMovies2Ratings
from py.postgres import Postgres

server = GLOBALS.PG_SERVER
port = GLOBALS.PG_PORT
db = GLOBALS.PG_DB_DEV
user = GLOBALS.PG_USERNAME
pw = GLOBALS.PG_PASSWORD

with open('test_data.json') as data_file:
    data = json.load(data_file)

class TestInsertMovies2Ratings(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ins = InsertMovies2Ratings(server, port, db, user, pw)
        cls.pg = Postgres(server, port, db, user, pw)
        sql = """insert into kino.movies (imdb_id, title, runtime, rated, released)
                 values ('tt2562232', 'Birdman or (The Unexpected Virtue of Ignorance)', '119 min', 'R', '14 Nov 2014')"""
        cls.pg.pg_cur.execute(sql)
        cls.pg.pg_conn.commit()

    def test_insert_movies(self):
        self.ins.insert(data)
        self.pg.pg_cur.execute('select imdb_id, source, rating from kino.movies2ratings')
        result = self.pg.pg_cur.fetchall()
        self.assertEqual(result, [('tt2562232', 'metascore', '88'),
                                  ('tt2562232', 'imdb', '7.8'),
                                  ('tt2562232', 'internet movie database', '7.8/10'),
                                  ('tt2562232', 'rotten tomatoes', '91%'),
                                  ('tt2562232', 'metacritic', '88/100')])

    @classmethod
    def tearDownClass(cls):
        cls.pg = Postgres(server, port, db, user, pw)
        cls.pg.pg_cur.execute('delete from kino.movies2ratings')
        cls.pg.pg_cur.execute('delete from kino.movies')
        cls.pg.pg_conn.commit()

if __name__ == '__main__':
    unittest.main()
