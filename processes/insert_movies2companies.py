import json

from processes.postgres import Postgres


def execute(data, pg: Postgres):
    """
    This inserts the relevant json information
    into the table kino.movies2companies.
    :param data: json data holding information on films.
    :param pg: Postgres connection object.
    """
    company_data = data['tmdb_company']

    # Insert into company roles.
    sql = '''insert into kino.company_roles (role)
             select 'Production'::text as role
                 on conflict on constraint company_roles_pkey
                 do nothing
          '''

    pg.pg_cur.execute(sql)
    pg.pg_conn.commit()

    # Insert in companies.
    sql = '''insert into kino.companies (name)
                select x.name
                  from json_to_recordset( %s) x (name varchar(1000))
                    on conflict on constraint companies_pkey
                    do nothing
             '''

    pg.pg_cur.execute(sql, (json.dumps(company_data),))
    pg.pg_conn.commit()

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

    pg.pg_cur.execute(sql, (json.dumps(company_data), ))
    pg.pg_conn.commit()

    return data
