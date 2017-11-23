import json
try:
    from postgres import Postgres
except ImportError:
    from inserts.postgres import Postgres


class InsertData(object):

    def __init__(self, server, port, database, username, password):
        self.pg = Postgres(server, port, database, username, password)
        self.source_topic = 'movies'
        self.destination_topic = 'movies2companies'

    def insert(self, data):
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
