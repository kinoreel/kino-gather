import unittest
import os
import json

from processes.insert_movies2companies import Main
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


class TestInsertMovies2Companies(unittest.TestCase):

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


    def test_insert_movies2companies(self):

        destination_data = self.main.run(data)

        # Inserted into kino.company_roles
        self.pg.pg_cur.execute('select role from kino.company_roles')
        result = self.pg.pg_cur.fetchall()
        self.assertEqual(result, [('Production',)])

        # Inserted into kino.companies
        self.pg.pg_cur.execute('select name from kino.companies')
        result = self.pg.pg_cur.fetchall()
        expected = [(e['name'],) for e in data['tmdb_company']]
        self.assertEqual(set(result),set(expected))

        # Inserted into kino.movies2companies
        sql = """select x.imdb_id, y.name, x.role
                   from kino.movies2companies x
                   join kino.companies y
                     on x.company_id = y.company_id"""
        self.pg.pg_cur.execute(sql)
        result = self.pg.pg_cur.fetchall()
        expected = [(e['imdb_id'], e['name'], 'Production') for e in data['tmdb_company']]
        self.assertEqual(set(result), set(expected))

        # Check that correctly return the data we need for the destination topic
        self.assertEqual(destination_data, None)

    @classmethod
    def tearDownClass(cls):
        cls.pg = Postgres(DB_SERVER, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD)
        cls.pg.pg_cur.execute('delete from kino.movies2companies')
        cls.pg.pg_cur.execute('delete from kino.companies')
        cls.pg.pg_cur.execute('delete from kino.company_roles')
        cls.pg.pg_cur.execute('delete from kino.movies')
        cls.pg.pg_conn.commit()

if __name__ == '__main__':
    unittest.main()
