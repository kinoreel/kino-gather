import json

from processes.postgres import Postgres


def execute(data, pg: Postgres):
    """
    This inserts the relevant json information
    into the table kino.movies2ratings.
    :param data: json data holding information on films.
    :param pg: Postgres connection object.
    """

    ratings_data = data['omdb_ratings']

    # We have to specify the tstamp, as the default value is only populated
    # when the insert is done via Django.
    sql = """insert into kino.movies2ratings (imdb_id, source, rating, tstamp)
             select imdb_id
                  , lower(source) as source
                  , value
                  , CURRENT_DATE
              from json_to_recordset(%s) x (imdb_id varchar(1000), source varchar(1000), value real)
              where ( imdb_id, lower(source) ) not in (select imdb_id
                                                     , source
                                                  from kino.movies2ratings )"""

    pg.pg_cur.execute(sql, (json.dumps(ratings_data), ))
    pg.pg_conn.commit()
