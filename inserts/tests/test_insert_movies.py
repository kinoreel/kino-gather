import json
import unittest
import datetime

from inserts import GLOBALS
from inserts.insert_movies import InsertData
from inserts.postgres import Postgres

server = GLOBALS.PG_SERVER
port = GLOBALS.PG_PORT
db = GLOBALS.PG_DB
user = GLOBALS.PG_USERNAME
pw = GLOBALS.PG_PASSWORD

with open('test_data.json') as data_file:
    data = json.load(data_file)

class TestInsertMovies(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ins = InsertData(server, port, db, user, pw)
        cls.pg = Postgres(server, port, db, user, pw)

    def test_insert_movies(self):
        self.ins.insert(data)
        self.pg.pg_cur.execute('select imdb_id, title, runtime, rated, released, orig_language from kino.movies')
        result = self.pg.pg_cur.fetchall()
        self.assertEqual(result,[('tt2562232', 'Birdman or (The Unexpected Virtue of Ignorance)', '119', 'R', datetime.date(2014, 8, 27), 'en')])

        self.pg.pg_cur.execute('select language from kino.languages')
        result = self.pg.pg_cur.fetchall()
        self.assertEqual(result, [('en',)])

    @classmethod
    def tearDownClass(cls):
        cls.pg = Postgres(server, port, db, user, pw)
        cls.pg.pg_cur.execute('delete from kino.languages')
        cls.pg.pg_cur.execute('delete from kino.movies')
        cls.pg.pg_conn.commit()

if __name__ == '__main__':
    unittest.main()
