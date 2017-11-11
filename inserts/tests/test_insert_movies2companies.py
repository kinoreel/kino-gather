import json
import unittest

from inserts import GLOBALS
from inserts.insert_movies2companies import InsertData
from inserts.postgres import Postgres

server = GLOBALS.PG_SERVER
port = GLOBALS.PG_PORT
db = GLOBALS.PG_DB
user = GLOBALS.PG_USERNAME
pw = GLOBALS.PG_PASSWORD

with open('test_data.json') as data_file:
    data = json.load(data_file)
    # select specific data to mirror the data found in
    # then source topic.
    data = {'tmdb_company': data['tmdb_company']}

class TestInsertMovies2Persons(unittest.TestCase):

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


    def test_insert_movies2companies(self):
        destination_data = self.ins.insert(data)

        # Inserted into kino.company_roles
        self.pg.pg_cur.execute('select role from kino.company_roles')
        result = self.pg.pg_cur.fetchall()
        self.assertEqual(result, [('Production',)])

        # Inserted into kino.companies
        self.pg.pg_cur.execute('select name from kino.companies')
        result = self.pg.pg_cur.fetchall()
        self.assertEqual(result, [('Worldview Entertainment',), ('New Regency Pictures',), ('TSG Entertainment',),
                                  ('Le Grisbi Productions',), ('M Productions',)])

        # Inserted into kino.movies2companies
        sql = """select x.imdb_id, y.name, x.role
                   from kino.movies2companies x
                   join kino.companies y
                     on x.company_id = y.company_id"""
        self.pg.pg_cur.execute(sql)
        result = self.pg.pg_cur.fetchall()
        self.assertEqual(result,[('tt2562232', 'Worldview Entertainment', 'Production'),
                                 ('tt2562232', 'New Regency Pictures', 'Production'),
                                 ('tt2562232', 'TSG Entertainment', 'Production'),
                                 ('tt2562232', 'Le Grisbi Productions', 'Production'),
                                 ('tt2562232', 'M Productions', 'Production')])

        # Check that correctly return the data we need for the destination topic
        self.assertEqual(destination_data, None)

    @classmethod
    def tearDownClass(cls):
        cls.pg = Postgres(server, port, db, user, pw)
        cls.pg.pg_cur.execute('delete from kino.movies2companies')
        cls.pg.pg_cur.execute('delete from kino.companies')
        cls.pg.pg_cur.execute('delete from kino.company_roles')
        cls.pg.pg_cur.execute('delete from kino.movies')
        cls.pg.pg_conn.commit()

if __name__ == '__main__':
    unittest.main()
