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
        self.destination_topic = 'movies2companies'

    def run(self, data):
        """
        This inserts the relevant json information
        into the table kino.movies.
        :param data: json data holding information on films.
        """

        company_data = data['tmdb_company']

        # Insert into company roles.
        sql = '''insert into kino.company_roles (role)
                 select 'Production'::text as role
                     on conflict on constraint company_roles_pkey
                     do nothing
              '''

        self.pg.pg_cur.execute(sql)

        # Insert in companies.
        sql = '''insert into kino.companies (name)
                    select x.name
                      from json_to_recordset( %s) x (name varchar(1000))
                        on conflict on constraint companies_pkey
                        do nothing
                 '''

        self.pg.pg_cur.execute(sql, (json.dumps(company_data),))

        # Insert movies2companies.
        sql = """ insert into kino.movies2companies(imdb_id, company_id, role)
                    select x.imdb_id
                         , y.company_id
                         , 'Production'::text as role
                      from json_to_recordset( %s) x (imdb_id varchar(1000), name varchar(1000))
                      join kino.companies y
                        on x.name = y.name
                     group by x.imdb_id
                         , y.company_id
                        on conflict
                        do nothing
                """

        self.pg.pg_cur.execute(sql, (json.dumps(company_data), ))
        self.pg.pg_conn.commit()
