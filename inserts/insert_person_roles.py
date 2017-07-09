import json
from postgres import Postgres


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

        sql = """insert into person_roles (role, tstamp)
                 select job
                      , CURRENT_DATE
                   from json_to_recordset( %s) x (job varchar(1000))
                  where (job) not in (select role
                                        from person_roles)
                  group by job"""

        self.pg.pg_cur.execute(sql, (json.dumps(crew_data), ))
        self.pg.pg_conn.commit()

        destination_data = {'tmdb_crew': data['tmdb_crew'],
                            'tmdb_cast': data['tmdb_cast']}

        # As we have created a new dictionary, we must transform it
        # into json before returning it to kafka, otherwise it
        # will be read by the next topid as a string.
        return destination_data

