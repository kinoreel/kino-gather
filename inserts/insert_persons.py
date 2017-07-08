import json

from postgres import Postgres


class InsertData(object):

    def __init__(self, server, port, database, username, password):
        self.pg = Postgres(server, port, database, username, password)
        self.source_topic = 'person_roles'
        self.destination_topic = 'persons'

    def insert(self, data):
        """
        This inserts the relevant json information
        into the table kino.movies.
        :param data: json data holding information on films.
        """

        crew_data = data['tmdb_crew']
        cast_data = data['tmdb_cast']

        sql = """insert into kino.persons (fullname, tstamp)
                 select z.name
                      , CURRENT_DATE
                   from ( select name
                            from json_to_recordset( %s) x (name varchar(1000))
                           union
                          select name
                            from  json_to_recordset( %s) y (name varchar(1000)) ) z
                 where z.name not in (select fullname
                                       from kino.persons )"""

        self.pg.pg_cur.execute(sql, (json.dumps(crew_data), json.dumps(cast_data)))
        self.pg.pg_conn.commit()

