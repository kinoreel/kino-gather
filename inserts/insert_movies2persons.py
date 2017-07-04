import json

from apis import GLOBALS
from py.postgres import Postgres


class InsertData(object):

    def __init__(self, server, port, database, username, password):
        self.pg = Postgres(server, port, database, username, password)
        self.source_topic = 'persons'
        self.destination_topic = 'movies2persons'

    def insert(self, data):
        """
        This inserts the relevant json information
        into the table kino.movies.
        :param data: json data holding information on films.
        """

        crew_data = data['tmdb_crew']
        cast_data = data['tmdb_cast']

        sql = """insert into movies2persons (imdb_id, person_id, role)
                 select x.imdb_id
                      , y.person_id
                      , x.job
                   from ( select imdb_id
                               , name
                               , 'Actor' as job
                            from json_to_recordset( %s) a (imdb_id varchar(1000), name varchar(1000))
                           union all
                          select imdb_id
                               , name
                               , job
                            from json_to_recordset(%s) b (imdb_id varchar(1000), name varchar(1000), job varchar(1000))
                        ) x
                   join kino.persons y
                     on x.name = y.fullname
                  where ( imdb_id, person_id, job ) not in ( select imdb_id
                                                                  , person_id
                                                                  , role
                                                               from kino.movies2persons )"""

        self.pg.pg_cur.execute(sql, (json.dumps(cast_data), json.dumps(crew_data)))
        self.pg.pg_conn.commit()
