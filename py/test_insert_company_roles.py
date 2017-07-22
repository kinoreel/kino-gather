import unittest
import json

from postgres import Postgres

from insert_company_roles import InsertData
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
        cls.ins = InsertData(port=port, database=db, username=user, password=pw, server=server)
        cls.pg.pg_cur.execute("delete from kino.company_roles")
        cls.pg.pg_conn.commit()



    def setUp(self):
        self.ins.insert(data)

    def test_count(self):
        self.pg.pg_cur.execute('select count(*) from kino.company_roles')
        result = self.pg.pg_cur.fetchall()
        print(result)
        self.assertEqual(result, [(1,)])

    def test_values(self):
        self.pg.pg_cur.execute('select role from kino.company_roles')
        result = self.pg.pg_cur.fetchall()
        print(result)
        self.assertEqual(result, [('Production',)])

    @classmethod
    def tearDown(cls):
        cls.pg = Postgres(server, port, db, user, pw)
        cls.pg.pg_cur.execute('delete from kino.company_roles')
        cls.pg.pg_conn.commit()


if __name__ == '__main__':
    unittest.main()



