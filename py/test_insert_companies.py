import unittest
import json

from postgres import Postgres

from insert_companies import InsertData
import GLOBALS


server = GLOBALS.PG_SERVER
port = GLOBALS.PG_PORT
db = GLOBALS.PG_DB_DEV
user = GLOBALS.PG_USERNAME
pw = GLOBALS.PG_PASSWORD

with open('test_json.json') as data_file:
    data = json.load(data_file)
    print('WE HAVE DATA')

class TestInsertMovies(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pg = Postgres(server, port, db, user, pw)
        cls.ins = InsertData(port=port, database=db, username=user, password=pw, server=server)
        cls.pg.pg_cur.execute("delete from kino.companies")
        cls.pg.pg_conn.commit()



    def setUp(self):
        self.ins.insert(data)

    def test_count(self):

        self.pg.pg_cur.execute('select count(*) from kino.companies')
        result = self.pg.pg_cur.fetchall()
        print(result)
        self.assertEqual(result, [(5,)])

    def test_values(self):
        self.pg.pg_cur.execute('select name from kino.companies')
        result = self.pg.pg_cur.fetchall()
        print(result)
        self.assertEqual(result, [('Worldview Entertainment',), ('New Regency Pictures',), ('TSG Entertainment',),
                                  ('Le Grisbi Productions',), ('M Productions',)])

    @classmethod
    def tearDownClass(cls):
        # We have to delete from kino_movies last, due to foreign key constraints
        cls.pg = Postgres(server, port, db, user, pw)
        sql = "delete from kino.companies"
        cls.pg.pg_cur.execute(sql)
        cls.pg.pg_conn.commit()



if __name__ == '__main__':
    print('testing start...')
    unittest.main()
