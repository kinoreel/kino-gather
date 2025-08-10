import json

from processes.postgres import Postgres


def execute(data, pg: Postgres):
    """
    This inserts the relevant json information
    into the table kino.movies2keywords.
    :param data: json data holding information on films.
    :param pg: Postgres connection object.
    """

    keyword_data = data['tmdb_keywords']
    # We have to specify the tstamp, as the default value is only populated
    # when the insert is done via Django.
    sql = """insert into kino.movies2keywords (imdb_id, keyword, tstamp)
             select imdb_id
                  , lower(keyword)
                  , CURRENT_DATE
               from json_to_recordset(%s) x (imdb_id varchar(1000), keyword varchar(100))
                 on conflict on constraint movies2keywords_pkey
                 do nothing"""
    pg.pg_cur.execute(sql, (json.dumps(keyword_data), ))
    pg.pg_conn.commit()
