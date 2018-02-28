import unittest
import os
import json

from processes.insert_movies2persons import Main
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


class TestInsertMovies2Persons(unittest.TestCase):

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


    def test_insert_movies2persons(self):
        destination_data = self.main.run(data)

        # Inserted into kino.person_roles
        self.pg.pg_cur.execute('select role from kino.person_roles')
        result = [e[0] for e in self.pg.pg_cur.fetchall()]
        expected = [e['role'] for e in (data['tmdb_crew'])] +[e['role'] for e in (data['tmdb_cast'])]
        self.assertEqual(set(result), set(expected))

        # Inserted into kino.persons
        self.pg.pg_cur.execute('select fullname from kino.persons')
        result = self.pg.pg_cur.fetchall()
        expected = [(e['name'],) for e in (data['tmdb_crew'])] + [(e['name'],) for e in (data['tmdb_cast'])]
        self.assertEqual(set(result), set(expected))

        # Inserted into kino.movies2persons
        sql = """select x.imdb_id, y.fullname, x.role, x.cast_order
                   from kino.movies2persons x
                   join kino.persons y
                     on x.person_id = y.person_id"""
        self.pg.pg_cur.execute(sql)
        result = self.pg.pg_cur.fetchall()
        expected = [(e['imdb_id'], e['name'], e['role'], None) for e in (data['tmdb_crew'])] + \
                   [(e['imdb_id'], e['name'], e['role'], e['cast_order']) for e in (data['tmdb_cast'])]
        self.assertEqual(set(result), set(expected))


    @classmethod
    def tearDownClass(cls):
        cls.pg = Postgres(DB_SERVER, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD)
        cls.pg.pg_cur.execute('delete from kino.movies2persons')
        cls.pg.pg_cur.execute('delete from kino.persons')
        cls.pg.pg_cur.execute('delete from kino.person_roles')
        cls.pg.pg_cur.execute('delete from kino.movies')
        cls.pg.pg_conn.commit()

if __name__ == '__main__':
    unittest.main()
