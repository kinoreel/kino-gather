import psycopg2


class Postgres(object):

    def __init__(self, server, port, database, username, password):

        dbconn = {'database': database,
                  'user': username,
                  'password': password,
                  'host': server,
                  'port': port}

        self.pg_conn = psycopg2.connect(**dbconn)
        self.pg_cur = self.pg_conn.cursor()
