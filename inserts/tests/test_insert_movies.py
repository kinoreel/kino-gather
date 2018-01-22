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
        # We test upsert by attempting to insert the data twice.
        self.ins.insert(data)
        self.ins.insert(data)
        self.pg.pg_cur.execute('select imdb_id, title, runtime, rated, released, orig_language, plot from kino.movies')
        result = self.pg.pg_cur.fetchall()
        self.assertEqual(result, [('tt2562232', 'Birdman', 119, 'R', datetime.date(2014, 8, 27), 'en', 'A fading actor best known for his portrayal of a popular superhero attempts to mount a comeback by appearing in a Broadway play. As opening night approaches, his attempts to become more altruistic, rebuild his career, and reconnect with friends and family prove more difficult than expected.')])

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
