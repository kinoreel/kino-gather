import json

try:
    from postgres import Postgres
except ImportError:
    from inserts.postgres import Postgres


class InsertData(object):

    def __init__(self, server, port, database, username, password):
        self.pg = Postgres(server, port, database, username, password)
        self.source_topic = 'errored'

    def insert(self, data):
        """
        This inserts the relevant json information about errors
        into the table kino.errors.
        :param data: json data holding information on films.
        """
        errored = data

        sql = """insert into kino.errored(imdb_id, error_message)
                 select x.imdb_id, x.error_message
                   from json_to_recordset(%s) x (imdb_id varchar(1000), error_message varchar(4000))
              """

        self.pg.pg_cur.execute(sql, (json.dumps(errored),))
        self.pg.pg_conn.commit()

        return data