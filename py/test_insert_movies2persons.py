import unittest
import json
import GLOBALS

from postgres import Postgres
from insert_movies2persons import InsertData

server = GLOBALS.PG_SERVER
port = GLOBALS.PG_PORT
db = GLOBALS.PG_DB_DEV
user = GLOBALS.PG_USERNAME
pw = GLOBALS.PG_PASSWORD

with open('test_data.json') as data_file:
    data = json.load(data_file)
    # select specific data to mirror the data found in
    # then source topic.
    data = {'tmdb_crew': data['tmdb_crew'],
            'tmdb_cast': data['tmdb_cast']}

class TestInsertMovies2Persons(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ins = InsertData(server, port, db, user, pw)
        cls.pg = Postgres(server, port, db, user, pw)
        # We insert the corresponding film into kino.movies
        # due to the foreign key constraint.
        sql = """insert into kino.movies (imdb_id, title, runtime, rated, released, orig_language)
                 values ('tt2562232', 'Birdman or (The Unexpected Virtue of Ignorance)', '119', 'R', '2014-08-27', 'en')"""
        cls.pg.pg_cur.execute(sql)
        cls.pg.pg_conn.commit()

    def test_insert_movies(self):
        destination_data = self.ins.insert(data)
        self.pg.pg_cur.execute('select fullname from kino.persons')
        result = self.pg.pg_cur.fetchall()
        print(result)
        self.assertEqual(result,[('Stephen Mirrione',), ('Alexander Dinelaris',),
                                 ('Alejandro González Iñárritu',), ('Michael Keaton',),
                                 ('Emma Stone',)])

        # Check that correctly return the data we need for the destination topic
        self.assertEqual(destination_data, json.dumps(data))

    @classmethod
    def tearDownClass(cls):
        cls.pg = Postgres(server, port, db, user, pw)
        cls.pg.pg_cur.execute('delete from kino.persons')
        cls.pg.pg_conn.commit()

if __name__ == '__main__':
    unittest.main()
