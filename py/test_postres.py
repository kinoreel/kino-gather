import unittest
import json

from postgres import Postgres

with open('db_auth.json') as auth_file:
    auth = json.load(auth_file)['postgres_dev']

class TestPostgres(unittest.TestCase):

    def test_connect(self):
        pg = Postgres(auth)

    def test_insert_tuples(self):
        pg = Postgres(auth)
        sql = 'create table ut_test_insert (col_1 varchar(10), col_2 smallint)'
        pg.pg_cur.execute(sql)
        data = [('test_1',1),('test_2', 2)]
        pg.insert_data('public', 'ut_test_insert', ['col_1', 'col_2'], data)
        pg.pg_cur.execute('select * from ut_test_insert')
        result = pg.pg_cur.fetchall()
        self.assertEqual(result, [('test_1', 1), ('test_2',2)])
        sql = 'drop table ut_test_insert'
        pg.pg_cur.execute(sql)

    def test_insert_json(self):
        pg = Postgres(auth)
        sql = 'create table ut_test_insert (col_1 varchar(10), col_2 smallint)'
        pg.pg_cur.execute(sql)
        data = [{'col_1':'test_1','col_2':1}, {'col_1':'test_2','col_2':2},]
        pg.insert_json('public', 'ut_test_insert', data)
        pg.pg_cur.execute('select * from ut_test_insert')
        result = pg.pg_cur.fetchall()
        self.assertEqual(result, [('test_1', 1), ('test_2', 2)])
        sql = 'drop table ut_test_insert'
        pg.pg_cur.execute(sql)


    def test_run_query_minus(self):
        pg = Postgres(auth)
        sql = 'create table ut_test_1(col_1 varchar(10), col_2 smallint)'
        pg.pg_cur.execute(sql)
        sql = 'create table ut_test_2(col_1 varchar(10), col_2 smallint)'
        pg.pg_cur.execute(sql)
        sql = "insert into ut_test_1 values ('test_1', 1)"
        pg.pg_cur.execute(sql)
        sql = "insert into ut_test_2 values ('test_1', 1)"
        pg.pg_cur.execute(sql)
        sql = "insert into ut_test_2 values ('test_2', 2)"
        pg.pg_cur.execute(sql)
        result = pg.run_query("select * from ut_test_2 except select * from ut_test_1")
        self.assertEqual(result, [('test_2', 2)])
        sql = 'drop table ut_test_1'
        pg.pg_cur.execute(sql)
        sql = 'drop table ut_test_2'
        pg.pg_cur.execute(sql)

if __name__ == '__main__':
    unittest.main()
