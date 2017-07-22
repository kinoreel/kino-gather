import json
from inserts.postgres import Postgres
from inserts import GLOBALS


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

        company_data = data['tmdb_companies']

        # Insert into company roles.
        sql = '''insert into kino.company_roles (role)
                 select 'Production'::text as role
                  where 'Production' not in (select role
                                               from kino.company_roles)
              '''

        self.pg.pg_cur.execute(sql)

        # Insert in companies.
        sql = '''insert into kino.companies (name)
                    select x.name
                      from json_to_recordset( %s) x (name varchar(1000))
                     where x.name not in (select name
                                            from kino.companies )
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
                      left join kino.movies2companies z
                        on y.company_id = z.company_id
                       and x.imdb_id = z.imdb_id
                     where z.imdb_id is null
                     group by x.imdb_id
                         , y.company_id
                """

        self.pg.pg_cur.execute(sql, (json.dumps(company_data), ))
        self.pg.pg_conn.commit()
