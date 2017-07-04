import unittest
import json

from postgres import Postgres

import insert_company_roles as cr
import insert_companies as co
import insert_movies2companies as m2c

import GLOBALS

server = GLOBALS.PG_SERVER
port = GLOBALS.PG_PORT
db = GLOBALS.PG_DB_DEV
user = GLOBALS.PG_USERNAME
pw = GLOBALS.PG_PASSWORD

with open('test_json.json') as data_file:
    data = json.load(data_file)
    print('WE HAVE DATA')

class TestInsertCoRoles(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pg = Postgres(server, port, db, user, pw)
        cls.coins = co.InsertData(port=port, database=db, username=user, password=pw, server=server)
        cls.crins = cr.InsertData(port=port, database=db, username=user, password=pw, server=server)
        cls.m2cins = m2c.InsertData(port=port, database=db, username=user, password=pw, server=server)
        cls.pg.pg_cur.execute("delete from kino.movies")
        cls.pg.pg_cur.execute("delete from kino.company_roles")
        cls.pg.pg_cur.execute("delete from kino.companies")
        cls.pg.pg_cur.execute("delete from kino.movies2companies")
        cls.pg.pg_conn.commit()



    def setUp(self):
        self.coins.insert(data)
        self.crins.insert(data)
        self.m2cins.insert(data)

    def test_count(self):
        self.pg.pg_cur.execute('select count(*) from kino.movies2companies')
        result = self.pg.pg_cur.fetchall()
        print(result)
        #self.assertEqual(result, [(1,)])

    def test_values(self):
        self.pg.pg_cur.execute('select role from kino.movies2companies')
        result = self.pg.pg_cur.fetchall()
        print(result)
        #self.assertEqual(result, [('Production',)])

    @classmethod
    def tearDown(cls):
        cls.pg = Postgres(server, port, db, user, pw)
        cls.pg.pg_cur.execute("delete from kino.movies2companies")
        cls.pg.pg_cur.execute("delete from kino.company_roles")
        cls.pg.pg_cur.execute("delete from kino.companies")
        cls.pg.pg_cur.execute("delete from kino.movies")
        cls.pg.pg_conn.commit()


if __name__ == '__main__':
    unittest.main()



