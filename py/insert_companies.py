import json
from postgres import Postgres
import GLOBALS


class InsertData(object):

    def __init__(self, server, port, database, username, password):
        self.pg = Postgres(server, port, database, username, password)
        self.source_topic = 'company_roles'
        self.destination_topic = 'companies'


    def insert(self, data):
        """
        This inserts the relevant json information
        into the table kino.movies.
        :param data: json data holding information on films.
        """

        tmdb_companies = data['tmdb_companies']

        sql = '''insert into kino.companies (name)
                    select y.name
                      from json_populate_recordset(NULL::kino.companies, %s) y
                      left join kino.companies x
                        on y.name = x.name
                     where x.name is null
                 '''

        self.pg.pg_cur.execute(sql, (json.dumps(tmdb_companies), ))
        self.pg.pg_conn.commit()

        return json.dumps(data)