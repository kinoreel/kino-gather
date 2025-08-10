import json

from processes.gather_exception import GatherException
from processes.postgres import Postgres


def execute(data, pg: Postgres):
    imdb_id = data['imdb_id']
    omdb_movie_data = data['omdb_main']
    tmdb_movie_data = data['tmdb_main']

    sql = """insert into kino.languages(language)
             select y.language
               from json_to_recordset(%s) x (original_language varchar(1000))
               join kino.iso2language y
                 on x.original_language = y.iso3166
              where language not in (select language
                                       from kino.languages)"""

    pg.pg_cur.execute(sql, (json.dumps(tmdb_movie_data),))
    pg.pg_conn.commit()

    # We delete our record from kino.movies first.
    # Due to foreign keys with 'on delete cascade', this clears all records from
    # the database associated with that imdb_id.

    sql = """delete from kino.movies
              where imdb_id = '{0}'""".format(imdb_id)

    pg.pg_cur.execute(sql)
    pg.pg_conn.commit()

    # We also delete any records in errored attached to this imdb_id, as
    # we have successfully gathered information for the film.

    sql = """delete from kino.errored
              where imdb_id = '{0}'""".format(imdb_id)

    pg.pg_cur.execute(sql)
    pg.pg_conn.commit()

    sql = """insert into kino.movies (imdb_id, title, runtime, rated, released, orig_language, plot, tstamp)
             select x.imdb_id
                  , y.title
                  , y.runtime
                  , x.rated
                  , y.release_date::date
                  , z.language
                  , y.plot
                  , CURRENT_DATE
               from json_to_recordset(%s) x ( imdb_id varchar(15), rated varchar(10) )
               join json_to_recordset(%s) y ( imdb_id varchar(15), title varchar(1000), runtime integer
                                            , release_date date, plot varchar(4000), original_language varchar(1000))
                 on x.imdb_id = y.imdb_id
               join kino.iso2language z
                 on y.original_language = z.iso3166
          """
    pg.pg_cur.execute(sql, (json.dumps(omdb_movie_data), json.dumps(tmdb_movie_data)))
    if pg.pg_cur.rowcount != 1:
        raise GatherException(omdb_movie_data[0]['imdb_id'], 'No insert into movies, most likely due to a new language')
    pg.pg_conn.commit()

    return data



