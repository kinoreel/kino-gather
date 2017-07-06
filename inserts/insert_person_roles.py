import json

from apis import GLOBALS
from py.postgres import Postgres


class InsertData(object):

    def __init__(self, server, port, database, username, password):
        self.pg = Postgres(server, port, database, username, password)
        self.source_topic = 'movies'
        self.destination_topic = 'person_roles'

    def insert(self, data):
        """
        This inserts the relevant json information
        into the table kino.movies.
        :param data: json data holding information on films.
        """

        crew_data = data['tmdb_crew']

        sql = """insert into movies_person_roles (role)
                 select job
                   from json_to_recordset( %s) x (job varchar(1000))
                  where (job) not in (select role
                                        from kino.person_roles)
                  group by job"""

        self.pg.pg_cur.execute(sql, (json.dumps(crew_data), ))
        self.pg.pg_conn.commit()

        destination_data = {'tmdb_crew': data['tmdb_crew'],
                            'tmdb_cast': data['tmdb_cast']}

        return json.dumps(destination_data)

