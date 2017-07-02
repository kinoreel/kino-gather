import unittest
import json
import GLOBALS

from postgres import Postgres
from insert_movies2genres import InsertMovies2Genres

server = GLOBALS.PG_SERVER
port = GLOBALS.PG_PORT
db = GLOBALS.PG_DB_DEV
user = GLOBALS.PG_USERNAME
pw = GLOBALS.PG_PASSWORD

with open('test_data.json') as data_file:
    data = json.load(data_file)

class TestInsertMovies2Genres(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ins = InsertMovies2Genres(server, port, db, user, pw)
        cls.pg = Postgres(server, port, db, user, pw)
        # We insert the corresponding film into kino.movies
        # due to the foreign key constraint.
        sql = """insert into kino.movies (imdb_id, title, runtime, rated, released)
                 values ('tt2562232', 'Birdman or (The Unexpected Virtue of Ignorance)', '119 min', 'R', '14 Nov 2014')"""
        cls.pg.pg_cur.execute(sql)
        cls.pg.pg_conn.commit()

    def test_insert_movies(self):
        self.ins.insert(data)
        self.pg.pg_cur.execute('select imdb_id, genre from kino.movies2genres')
        result = self.pg.pg_cur.fetchall()
        self.assertEqual(result, [('tt2562232', 'Drama'), ('tt2562232', 'Comedy')])

    @classmethod
    def tearDownClass(cls):
        cls.pg = Postgres(server, port, db, user, pw)
        cls.pg.pg_cur.execute('delete from kino.movies2genres')
        cls.pg.pg_cur.execute('delete from kino.movies')
        cls.pg.pg_conn.commit()

if __name__ == '__main__':
    unittest.main()
