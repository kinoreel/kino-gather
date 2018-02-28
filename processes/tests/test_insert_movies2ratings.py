import unittest
import os
import json

from processes.insert_movies2ratings import Main
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

with open('test_data.json') as data_file:
    data = json.load(data_file)


class TestInsertMovies2Ratings(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.main = Main()
        cls.pg = Postgres(DB_SERVER, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD)
        sql = """insert into kino.movies (imdb_id, title, runtime, rated, released, orig_language, plot)
                 values ('tt2562232', 'Birdman or (The Unexpected Virtue of Ignorance)', 119, 'R', '2014-08-27',
                         'en', 'Some plot')"""

        cls.pg.pg_cur.execute(sql)
        cls.pg.pg_conn.commit()

    def test_insert_movies(self):
        self.main.run(data)
        self.pg.pg_cur.execute('select imdb_id, source, rating from kino.movies2ratings')
        result = self.pg.pg_cur.fetchall()
        expected = [('tt2562232', 'imdb', 7.8),
                    ('tt2562232', 'metacritic', 88.0),
                    ('tt2562232', 'metascore', 88.0),
                    ('tt2562232', 'rotten tomatoes', 91.0),
                    ('tt2562232', 'internet movie database', 7.8)]
        self.assertEqual(set(result), set(expected))

    @classmethod
    def tearDownClass(cls):
        cls.pg = Postgres(DB_SERVER, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD)
        cls.pg.pg_cur.execute('delete from kino.movies2ratings')
        cls.pg.pg_cur.execute('delete from kino.movies')
        cls.pg.pg_conn.commit()

if __name__ == '__main__':
    unittest.main()
