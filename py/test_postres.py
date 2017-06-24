import unittest

from postgres import Postgres

from py import GLOBALS

auth = GLOBALS.POSTGRES_DEV

#TODO: Move to test folder
class TestPostgres(unittest.TestCase):

    def setUp(self):
        self.pg = Postgres(auth)

    def test_insert_tuples(self):
        sql = 'create table ut_test_insert (col_1 varchar(10), col_2 smallint)'
        self.pg.pg_cur.execute(sql)
        data = [('test_1',1),('test_2', 2)]
        self.pg.insert_data('public', 'ut_test_insert', ['col_1', 'col_2'], data)
        self.pg.pg_cur.execute('select * from ut_test_insert')
        result = self.pg.pg_cur.fetchall()
        self.assertEqual(result, [('test_1', 1), ('test_2',2)])
        sql = 'drop table ut_test_insert'
        self.pg.pg_cur.execute(sql)

    def test_insert_json(self):
        sql = 'create table ut_test_insert (col_1 varchar(10), col_2 smallint)'
        self.pg.pg_cur.execute(sql)
        data = [{'col_1':'test_1','col_2':1}, {'col_1':'test_2','col_2':2},]
        self.pg.insert_json('public', 'ut_test_insert', 'col_1, col_2', data)
        self.pg.pg_cur.execute('select * from ut_test_insert')
        result = self.pg.pg_cur.fetchall()
        self.assertEqual(result, [('test_1', 1), ('test_2', 2)])
        sql = 'drop table ut_test_insert'
        self.pg.pg_cur.execute(sql)
        self.pg.pg_conn.commit()

    def test_run_query_minus(self):
        sql = 'create table ut_test_1(col_1 varchar(10), col_2 smallint)'
        self.pg.pg_cur.execute(sql)
        sql = 'create table ut_test_2(col_1 varchar(10), col_2 smallint)'
        self.pg.pg_cur.execute(sql)
        sql = "insert into ut_test_1 values ('test_1', 1)"
        self.pg.pg_cur.execute(sql)
        sql = "insert into ut_test_2 values ('test_1', 1)"
        self.pg.pg_cur.execute(sql)
        sql = "insert into ut_test_2 values ('test_2', 2)"
        self.pg.pg_cur.execute(sql)
        result = self.pg.run_query("select * from ut_test_2 except select * from ut_test_1")
        self.assertEqual(result, [('test_2', 2)])
        sql = 'drop table ut_test_1'
        self.pg.pg_cur.execute(sql)
        sql = 'drop table ut_test_2'
        self.pg.pg_cur.execute(sql)

if __name__ == '__main__':
    unittest.main()
