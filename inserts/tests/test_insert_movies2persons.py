import json
import unittest

from inserts import GLOBALS
from inserts.insert_movies2persons import InsertData
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


    def test_insert_movies2persons(self):
        destination_data = self.ins.insert(data)

        # Inserted into kino.person_roles
        self.pg.pg_cur.execute('select role from kino.person_roles')
        result = self.pg.pg_cur.fetchall()
        self.assertEqual(result,[('Screenplay',), ('Director',), ('Editor',)])

        # Inserted into kino.persons
        self.pg.pg_cur.execute('select fullname from kino.persons')
        result = self.pg.pg_cur.fetchall()
        self.assertEqual(result,[('Stephen Mirrione',), ('Alexander Dinelaris',),
                                 ('Alejandro González Iñárritu',), ('Michael Keaton',),
                                 ('Emma Stone',)])

        # Inserted into kino.movies2persons
        sql = """select x.imdb_id, y.fullname, x.role
                   from kino.movies2persons x
                   join kino.persons y
                     on x.person_id = y.person_id"""
        self.pg.pg_cur.execute(sql)
        result = self.pg.pg_cur.fetchall()
        self.assertEqual(result,[('tt2562232', 'Michael Keaton', 'Actor'),
                                 ('tt2562232', 'Emma Stone', 'Actor'),
                                 ('tt2562232', 'Stephen Mirrione', 'Editor'),
                                 ('tt2562232', 'Alejandro González Iñárritu', 'Director'),
                                 ('tt2562232', 'Alexander Dinelaris', 'Screenplay')])

        # Check that correctly return the data we need for the destination topic
        self.assertEqual(destination_data, None)

    @classmethod
    def tearDownClass(cls):
        cls.pg = Postgres(server, port, db, user, pw)
        cls.pg.pg_cur.execute('delete from kino.movies2persons')
        cls.pg.pg_cur.execute('delete from kino.persons')
        cls.pg.pg_cur.execute('delete from kino.person_roles')
        cls.pg.pg_cur.execute('delete from kino.movies')
        cls.pg.pg_conn.commit()

if __name__ == '__main__':
    unittest.main()
