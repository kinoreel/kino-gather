import json
import os

from processes.postgres import Postgres


try:
    DB_SERVER = os.environ['DB_SERVER']
    DB_PORT = os.environ['DB_PORT']
    DB_DATABASE = os.environ['DB_DATABASE']
    DB_USER = os.environ['DB_USER']
    DB_PASSWORD = os.environ['DB_PASSWORD']
except KeyError:
    try:
        from processes.GLOBALS import DB_SERVER, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD
    except ImportError:
        print("No parameters provided")
        exit()


class Main(object):

    def __init__(self):
        self.pg = Postgres(DB_SERVER, DB_PORT, DB_DATABASE, DB_USER, DB_PASSWORD)
        self.source_topic = 'movies'
        self.destination_topic = 'movies2persons'

    def run(self, data):
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
                  from ( select role
                           from json_to_recordset( %s) x (role varchar(1000))
                          union
                         select role
                           from json_to_recordset( %s) x (role varchar(1000)) ) as roles
                  where (role) not in (select role
                                         from kino.person_roles)
                  group by role"""

        self.pg.pg_cur.execute(sql, (json.dumps(crew_data), json.dumps(cast_data)))
        self.pg.pg_conn.commit()

        # Insert into kino.persons.
        sql = """insert into kino.persons (fullname, tstamp)
                 select z.name
                      , CURRENT_DATE
                   from ( select name
                            from json_to_recordset( %s) x (name varchar(1000))
                           group by name
                           union
                          select name
                            from  json_to_recordset( %s) y (name varchar(1000))
                           group by name
                         ) z
                 where z.name not in (select fullname
                                       from kino.persons )"""

        self.pg.pg_cur.execute(sql, (json.dumps(crew_data), json.dumps(cast_data)))
        self.pg.pg_conn.commit()

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
                     on conflict on constraint movies2persons_pkey
                     do nothing"""

        self.pg.pg_cur.execute(sql, (json.dumps(cast_data), json.dumps(crew_data)))
        self.pg.pg_conn.commit()


