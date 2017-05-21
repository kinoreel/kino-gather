import psycopg2
import json

from psycopg2.extras import execute_values, Json

class Postgres:

    def __init__(self, auth):

        self.pg_conn = psycopg2.connect(auth)
        self.pg_cur = self.pg_conn.cursor()

    def insert_data(self, schema, table, cols, data):
        '''
        Inserts a list of tuples into the database.
        :param schema: The schema out table we are inserting into sits on
        :param table: The table we are inserting our data into
        :param cols: A tuple containing the columns of our data
        :param data: A list of tuples containing the data we want to insert
        '''
        cols =  (', '.join(cols))
        sql = 'insert into {0}.{1} ({2}) values %s'.format(schema, table, cols)
        psycopg2.extras.execute_values( self.pg_cur, sql, data, template=None, page_size=100)
        self.pg_conn.commit()

    def insert_json(self, schema, table, columns, data):
        '''
        Inserts a json data into the database
        :param schema: The schema out table we are inserting into sits on
        :param table: The table we are inserting our data into
        :param data: Json data in the format [{col_1:value_1, col_2:value_2, ...},{...} }]
        :return:
        '''
        sql = "insert into {0}.{1} " \
              "select {2}" \
              "  from json_populate_recordset( NULL::{0}.{1}, %s)".format(schema, table, columns)
        self.pg_cur.execute(sql, (json.dumps(data), ))

    def select_data(self, schema, table, cols):
        '''
        This returns data from a table
        :param table: The table we are inserting into on kino@kino
        :param cols: A tuple containing the columns of our data
        :param data: A list of tuples containing the data we want to insert
        '''
        cols = (', '.join(cols))
        sql = 'select {2} from {0}.{1}'.format(schema, table, cols)
        self.pg_cur.execute(sql)
        result = self.pg_cur.fetchall()
        return result

    def run_query(self, sql):
        self.pg_cur.execute(sql)
        result = self.pg_cur.fetchall()
        return result


if __name__=='__main__':
    pg = Postgres()
