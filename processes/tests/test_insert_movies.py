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
        # Insert 'old/incorrect' information into kino tables, to check that inserting into movies,
        # removes all previously stored data

        # movies
        self.pg.pg_cur.execute("insert into movies values"
                               " ('tt2562232', 'invalid', 0, 'N/A',  '2000-01-01', 'invalid', 'invalid')")
        # movies2companies
        self.pg.pg_cur.execute("insert into companies values (0, 'invalid')")
        self.pg.pg_cur.execute("insert into movies2companies values"
                               " ('tt2562232', 0, 'invalid')")
        # movies2genres
        self.pg.pg_cur.execute("insert into genres values ('invalid')")
        self.pg.pg_cur.execute("insert into movies2genres values"
                               " ('tt2562232', 'invalid')")
        # movies2keywords
        self.pg.pg_cur.execute("insert into movies2keywords values"
                               " ('tt2562232', 'invalid')")
        # movies2persons
        self.pg.pg_cur.execute("insert into persons (person_id, fullname) values (0, 'invalid')")
        self.pg.pg_cur.execute("insert into movies2persons values"
                               " ('tt2562232', 0, 'invalid', null)")
        # movies2ratings
        self.pg.pg_cur.execute("insert into movies2ratings values"
                               " ('tt2562232', 'invalid', 0)")
        # movies2streams
        self.pg.pg_cur.execute("insert into movies2streams values"
                               " ('tt2562232', 'invalid', 'invalid', '$', 0.00, 'hd', 'rental')")
        # movies2trailer
        self.pg.pg_cur.execute("insert into movies2trailers values "
                               " ( 'tt2562232', 'invalid', 'invalid', 'invalid', 'invalid', 'in'"
                               " , 0, 0, 0, 0, 0, null)")

        # errored
        self.pg.pg_cur.execute("insert into errored values ( 'tt2562232', 'invalid')")

        self.pg.pg_conn.commit()

        # Run the insert
        self.ins.insert(data)

        # Check that correct information has been populated in movies
        self.pg.pg_cur.execute('select imdb_id, title, runtime, rated, released, orig_language, plot from kino.movies')

        result = self.pg.pg_cur.fetchall()
        self.assertEqual(result, [('tt2562232', 'Birdman', 119, 'R', datetime.date(2014, 8, 27), 'English',
                                   'A fading actor best known for his portrayal of a popular superhero attempts to '
                                   'mount a comeback by appearing in a Broadway play. As opening night approaches, '
                                   'his attempts to become more altruistic, rebuild his career, and reconnect with '
                                   'friends and family prove more difficult than expected.')])

        self.pg.pg_cur.execute('select language from kino.languages')
        result = self.pg.pg_cur.fetchall()
        self.assertEqual(result, [('English',)])

        # Check that all other information for this imdb_id has been removed from the
        # kino tables
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
        self.pg.pg_cur.execute('select count(*) from kino.errored')
        self.assertEqual([(0,)], self.pg.pg_cur.fetchall())


    @classmethod
    def tearDownClass(cls):
        cls.pg = Postgres(server, port, db, user, pw)
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
