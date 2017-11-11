import json

try:
    from postgres import Postgres
except ImportError:
    from inserts.postgres import Postgres


class InsertData(object):

    def __init__(self, server, port, database, username, password):
        self.pg = Postgres(server, port, database, username, password)
        self.source_topic = 'movies'
        self.destination_topic = 'movies2persons'

    def insert(self, data):
        """
        This inserts the relevant json information
        into the table kino.person_roles, kino.persons, kino.movies2persons.
        We insert in a specific order, due to the foreign keys on our database.
        :param data: json data holding information on films.
        """

        crew_data = data['tmdb_crew']
        cast_data = data['tmdb_cast']

        # Insert into kino.person_roles.
        sql = """insert into kino.person_roles (role, tstamp)
                select role
                     , CURRENT_DATE
                  from json_to_recordset( %s) x (role varchar(1000))
                 where (role) not in (select role
                                       from kino.person_roles)
                 group by role"""

        self.pg.pg_cur.execute(sql, (json.dumps(crew_data), ))


        # Insert into kino.persons.
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

        # Insert into kino.movies2persons
        sql = """insert into kino.movies2persons (imdb_id, person_id, role, cast_order, tstamp)
                 select x.imdb_id
                      , y.person_id
                      , x.role
                      , x.cast_order
                      , CURRENT_DATE
                   from ( select imdb_id
                               , name
                               , 'actor' as role
                               , cast_order
                            from json_to_recordset( %s) a (imdb_id varchar(1000), name varchar(1000), cast_order integer)
                           union all
                          select imdb_id
                               , name
                               , role
                               , null
                            from json_to_recordset(%s) b (imdb_id varchar(1000), name varchar(1000), role varchar(1000))
                        ) x
                   join kino.persons y
                     on x.name = y.fullname
                  where ( imdb_id, person_id, role ) not in ( select imdb_id
                                                                  , person_id
                                                                  , role
                                                               from kino.movies2persons )"""

        self.pg.pg_cur.execute(sql, (json.dumps(cast_data), json.dumps(crew_data)))

        self.pg.pg_conn.commit()


