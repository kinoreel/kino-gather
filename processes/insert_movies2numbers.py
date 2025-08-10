import json

from processes.postgres import Postgres


def execute(data, pg: Postgres):
    """
    This inserts the relevant json information
    into the table kino.movies2numbers.
    :param data: json data holding information on films.
    :param pg: Postgres connection object.
    """

    movie_data = data['tmdb_main']

    # We have to specify the tstamp, as the default value is only populated
    # when the insert is done via Django.
    sql = """insert into kino.movies2numbers (imdb_id, type, value, tstamp)
             with pivoted_data as (
             select imdb_id
                  , unnest(array['revenue', 'budget']) as type
                  , unnest(array[revenue, budget]) as value
               from json_to_recordset( %s) x (imdb_id varchar(1000), revenue int, budget int)
             )
             select imdb_id
                  , type
                  , value
                  , CURRENT_DATE
               from pivoted_data
              where ( imdb_id, type ) not in (select imdb_id
                                                   , type
                                                from kino.movies2numbers)"""

    pg.pg_cur.execute(sql, (json.dumps(movie_data), ))
    pg.pg_conn.commit()

