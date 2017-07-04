import unittest
import json
import GLOBALS

from postgres import Postgres
from insert_person_roles import InsertData

server = GLOBALS.PG_SERVER
port = GLOBALS.PG_PORT
db = GLOBALS.PG_DB_DEV
user = GLOBALS.PG_USERNAME
pw = GLOBALS.PG_PASSWORD

with open('test_data.json') as data_file:
    data = json.load(data_file)

class TestInsertPersonRoles(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ins = InsertData(server, port, db, user, pw)
        cls.pg = Postgres(server, port, db, user, pw)

    def test_insert_movies(self):
        destination_data = self.ins.insert(data)
        self.pg.pg_cur.execute('select role from kino.person_roles')
        result = self.pg.pg_cur.fetchall()
        self.assertEqual(result,[('Screenplay',), ('Director',), ('Editor',)])

        # Check that correctly return the data we need for the destination topic
        data_to_return = {'tmdb_crew': data['tmdb_crew'],
                          'tmdb_cast': data['tmdb_cast']}

        self.assertEqual(destination_data, json.dumps(data_to_return))

    @classmethod
    def tearDownClass(cls):
        cls.pg = Postgres(server, port, db, user, pw)
        cls.pg.pg_cur.execute('delete from kino.person_roles')
        cls.pg.pg_conn.commit()

if __name__ == '__main__':
    unittest.main()
