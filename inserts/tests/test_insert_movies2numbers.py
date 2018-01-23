import json
import unittest

from inserts import GLOBALS
from inserts.insert_movies2numbers import InsertData
from inserts.postgres import Postgres

server = GLOBALS.PG_SERVER
port = GLOBALS.PG_PORT
db = GLOBALS.PG_DB
user = GLOBALS.PG_USERNAME
pw = GLOBALS.PG_PASSWORD

with open('test_data.json') as data_file:
    data = json.load(data_file)


class TestInsertMovies2Numbers(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ins = InsertData(server, port, db, user, pw)
        cls.pg = Postgres(server, port, db, user, pw)
        # We insert the corresponding film into kino.movies
        # due to the foreign key constraint.
        sql = """insert into kino.movies (imdb_id, title, runtime, rated, released, orig_language, plot)
            values ('tt2562232', 'Birdman or (The Unexpected Virtue of Ignorance)', 119, 'R', '2014-08-27', 'en', 'Some plot')"""
        cls.pg.pg_cur.execute(sql)
        cls.pg.pg_conn.commit()

    def test_insert_movies(self):
        self.ins.insert(data)
        self.pg.pg_cur.execute('select imdb_id, value, type from kino.movies2numbers')
        result = self.pg.pg_cur.fetchall()
        expected = [(data['tmdb_main'][0]['imdb_id'], data['tmdb_main'][0]['revenue'], 'revenue'),
                    (data['tmdb_main'][0]['imdb_id'], data['tmdb_main'][0]['budget'], 'budget')]
        self.assertEqual(set(result), set(expected))


    @classmethod
    def tearDownClass(cls):
        cls.pg = Postgres(server, port, db, user, pw)
        cls.pg.pg_cur.execute('delete from kino.movies2numbers')
        cls.pg.pg_cur.execute('delete from kino.movies')
        cls.pg.pg_conn.commit()

if __name__ == '__main__':
    unittest.main()