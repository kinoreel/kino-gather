import json
from postgres import Postgres
import GLOBALS


class InsertData(object):

    def __init__(self, server, port, database, username, password):
        self.pg = Postgres(server, port, database, username, password)
        self.source_topic = 'movies'
        self.destination_topic = 'company_roles'


    def insert(self, data):
        """
        This inserts the relevant json information
        into the table kino.company_roles.
        :param data: json data holding information on films.
        """

        table = data['tmdb_companies']

        sql = '''insert into kino.company_roles (role)
                 select 'Production'::text as role
                  where 'Production' not in (select role
                                               from kino.company_roles)
              '''

        self.pg.pg_cur.execute(sql)
        self.pg.pg_conn.commit()

        return json.dumps(data)