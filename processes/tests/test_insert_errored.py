import unittest
import os

from processes.insert_errored import Main
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

data = [{'imdb_id': 'tt1234567', 'error_message': 'ERROR'}]


class TestInsertMovies(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.main = Main()
        cls.pg = Postgres(DB_SERVER, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD)

    def test_insert_movies(self):
        # Insert 'old/incorrect' information into kino tables, to check that inserting into errored
        # removes all previously stored data

        # movies
        self.pg.pg_cur.execute("insert into movies values"
                               " ('tt1234567', 'invalid', 0, 'N/A',  '2000-01-01', 'invalid', 'invalid')")
        # movies2companies
        self.pg.pg_cur.execute("insert into companies values (0, 'invalid')")
        self.pg.pg_cur.execute("insert into movies2companies values"
                               " ('tt1234567', 0, 'invalid')")
        # movies2genres
        self.pg.pg_cur.execute("insert into genres values ('invalid')")
        self.pg.pg_cur.execute("insert into movies2genres values"
                               " ('tt1234567', 'invalid')")
        # movies2keywords
        self.pg.pg_cur.execute("insert into movies2keywords values"
                               " ('tt1234567', 'invalid')")
        # movies2persons
        self.pg.pg_cur.execute("insert into persons (person_id, fullname) values (0, 'invalid')")
        self.pg.pg_cur.execute("insert into movies2persons values"
                               " ('tt1234567', 0, 'invalid', null)")
        # movies2ratings
        self.pg.pg_cur.execute("insert into movies2ratings values"
                               " ('tt1234567', 'invalid', 0)")
        # movies2streams
        self.pg.pg_cur.execute("insert into movies2streams values"
                               " ('tt1234567', 'invalid', 'invalid', '$', 0.00, 'hd', 'rental')")
        # movies2trailer
        self.pg.pg_cur.execute("insert into movies2trailers values "
                               " ('tt1234567', 'invalid', 'invalid', 'invalid', 'invalid', 'in'"
                               " , 0, 0, 0, 0, 0, null)")

        # errored
        self.pg.pg_cur.execute("insert into errored values ( 'tt1234567', 'invalid')")

        self.pg.pg_conn.commit()

        # Run the insert
        self.main.run(data)

        self.pg.pg_cur.execute('select imdb_id, error_message from kino.errored')
        result = self.pg.pg_cur.fetchall()
        expected = [('tt1234567', 'ERROR')]
        self.assertEqual(result, expected )

        # Check that all other information for this imdb_id has been removed from the
        # kino tables
        self.pg.pg_cur.execute('select count(*) from kino.movies')
        self.assertEqual([(0,)], self.pg.pg_cur.fetchall())
        self.pg.pg_cur.execute('select count(*) from kino.movies2companies')
        self.assertEqual([(0,)], self.pg.pg_cur.fetchall())
        self.pg.pg_cur.execute('select count(*) from kino.movies2genres')
        self.assertEqual([(0,)], self.pg.pg_cur.fetchall())
        self.pg.pg_cur.execute('select count(*) from kino.movies2numbers')
        self.assertEqual([(0,)], self.pg.pg_cur.fetchall())
        self.pg.pg_cur.execute('select count(*) from kino.movies2persons')
        self.assertEqual([(0,)], self.pg.pg_cur.fetchall())
        self.pg.pg_cur.execute('select count(*) from kino.movies2ratings')
        self.assertEqual([(0,)], self.pg.pg_cur.fetchall())
        self.pg.pg_cur.execute('select count(*) from kino.movies2streams')
        self.assertEqual([(0,)], self.pg.pg_cur.fetchall())
        self.pg.pg_cur.execute('select count(*) from kino.movies2trailers')
        self.assertEqual([(0,)], self.pg.pg_cur.fetchall())

    @classmethod
    def tearDownClass(cls):
        cls.pg = Postgres(DB_SERVER, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD)
        cls.pg.pg_cur.execute('delete from kino.languages')
        cls.pg.pg_cur.execute('delete from kino.movies')
        cls.pg.pg_cur.execute('delete from kino.movies2companies')
        cls.pg.pg_cur.execute('delete from kino.companies')
        cls.pg.pg_cur.execute('delete from kino.genres')
        cls.pg.pg_cur.execute('delete from kino.movies2genres')
        cls.pg.pg_cur.execute('delete from kino.movies2numbers')
        cls.pg.pg_cur.execute('delete from kino.movies2persons')
        cls.pg.pg_cur.execute('delete from kino.persons')
        cls.pg.pg_cur.execute('delete from kino.movies2ratings')
        cls.pg.pg_cur.execute('delete from kino.movies2streams')
        cls.pg.pg_cur.execute('delete from kino.movies2trailers')
        cls.pg.pg_cur.execute('delete from kino.errored')
        cls.pg.pg_conn.commit()

if __name__ == '__main__':
    unittest.main()
