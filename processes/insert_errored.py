import json

from processes.postgres import Postgres


class Main(object):

    def __init__(self, server, port, database, username, password):
        self.pg = Postgres(server, port, database, username, password)
        self.source_topic = 'errored'
        self.destination_topic = 'DONE'

    def run(self, data):
        """
        This inserts the relevant json information about errors
        into the table kino.errors.
        :param data: json data holding information on films.
        """

        # We delete our record from kino.movies first.
        # Due to foreign keys with 'on delete cascade', this clears all records from
        # the database associated with that imdb_id.
        imdb_id = data[0]['imdb_id']

        sql = """delete from kino.movies
                  where imdb_id = '{0}'""".format(imdb_id)
        self.pg.pg_cur.execute(sql)
        self.pg.pg_conn.commit()

        sql = """insert into kino.errored(imdb_id, error_message)
                 select x.imdb_id, x.error_message
                   from json_to_recordset(%s) x (imdb_id varchar(1000), error_message varchar(4000))
                     on conflict (imdb_id)
                     do update
                   set error_message = excluded.error_message
              """
        self.pg.pg_cur.execute(sql, (json.dumps(data),))
        self.pg.pg_conn.commit()

        return data