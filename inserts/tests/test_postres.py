import unittest

from inserts.postgres import Postgres

from inserts import GLOBALS

server = GLOBALS.PG_SERVER
port = GLOBALS.PG_PORT
db = GLOBALS.PG_DB_DEV
user = GLOBALS.PG_USERNAME
pw = GLOBALS.PG_PASSWORD

class TestPostgres(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pg = Postgres(server, port, db, user, pw)
        cls.pg.pg_cur.execute('create schema test')
        cls.pg.pg_conn.commit()

    def test_insert_tuples(cls):
        sql = 'create table test.ut_test_insert (col_1 varchar(10), col_2 smallint)'
        cls.pg.pg_cur.execute(sql)
        data = [('test_1',1),('test_2', 2)]
        cls.pg.insert_data('test', 'ut_test_insert', ['col_1', 'col_2'], data)
        cls.pg.pg_cur.execute('select * from test.ut_test_insert')
        result = cls.pg.pg_cur.fetchall()
        cls.assertEqual(result, [('test_1', 1), ('test_2',2)])
        sql = 'drop table test.ut_test_insert'
        cls.pg.pg_cur.execute(sql)
        cls.pg.pg_conn.commit()

    def test_insert_json(cls):
        sql = 'create table test.ut_test_insert (col_1 varchar(10), col_2 smallint)'
        cls.pg.pg_cur.execute(sql)
        data = [{'col_1':'test_1','col_2':1}, {'col_1':'test_2','col_2':2},]
        cls.pg.insert_json('test', 'ut_test_insert', 'col_1, col_2', data)
        cls.pg.pg_cur.execute('select * from test.ut_test_insert')
        result = cls.pg.pg_cur.fetchall()
        cls.assertEqual(result, [('test_1', 1), ('test_2', 2)])
        sql = 'drop table test.ut_test_insert'
        cls.pg.pg_cur.execute(sql)
        cls.pg.pg_conn.commit()

    def test_run_query_minus(cls):
        sql = 'create table test.ut_test_1(col_1 varchar(10), col_2 smallint)'
        cls.pg.pg_cur.execute(sql)
        sql = 'create table test.ut_test_2(col_1 varchar(10), col_2 smallint)'
        cls.pg.pg_cur.execute(sql)
        sql = "insert into test.ut_test_1 values ('test_1', 1)"
        cls.pg.pg_cur.execute(sql)
        sql = "insert into test.ut_test_2 values ('test_1', 1)"
        cls.pg.pg_cur.execute(sql)
        sql = "insert into test.ut_test_2 values ('test_2', 2)"
        cls.pg.pg_cur.execute(sql)
        result = cls.pg.run_query("select * from test.ut_test_2 except select * from test.ut_test_1")
        cls.assertEqual(result, [('test_2', 2)])
        sql = 'drop table test.ut_test_1'
        cls.pg.pg_cur.execute(sql)
        sql = 'drop table test.ut_test_2'
        cls.pg.pg_cur.execute(sql)
        cls.pg.pg_conn.commit()

    @classmethod
    def tearDownClass(cls):
        cls.pg = Postgres(server, port, db, user, pw)
        cls.pg.pg_cur.execute('drop schema test cascade')
        cls.pg.pg_conn.commit()


if __name__ == '__main__':
    unittest.main()
