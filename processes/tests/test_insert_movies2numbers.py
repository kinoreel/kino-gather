import unittest
import os
import json

from processes.insert_movies2numbers import Main
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


class TestInsertMovies2Numbers(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.main = Main()
        cls.pg = Postgres(DB_SERVER, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD)
        # We insert the corresponding film into kino.movies
        # due to the foreign key constraint.
        sql = """insert into kino.movies (imdb_id, title, runtime, rated, released, orig_language, plot)
            values ('tt2562232', 'Birdman or (The Unexpected Virtue of Ignorance)', 119, 'R', '2014-08-27', 'en', 'Some plot')"""
        cls.pg.pg_cur.execute(sql)
        cls.pg.pg_conn.commit()

    def test_insert_movies(self):
        self.main.run(data)
        self.pg.pg_cur.execute('select imdb_id, value, type from kino.movies2numbers')
        result = self.pg.pg_cur.fetchall()
        expected = [(data['tmdb_main'][0]['imdb_id'], data['tmdb_main'][0]['revenue'], 'revenue'),
                    (data['tmdb_main'][0]['imdb_id'], data['tmdb_main'][0]['budget'], 'budget')]
        print(set(result))
        print(set(expected))
        self.assertEqual(set(result), set(expected))


    @classmethod
    def tearDownClass(cls):
        cls.pg = Postgres(DB_SERVER, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD)
        cls.pg.pg_cur.execute('delete from kino.movies2numbers')
        cls.pg.pg_cur.execute('delete from kino.movies')
        cls.pg.pg_conn.commit()

if __name__ == '__main__':
    unittest.main()