import json

from processes.postgres import Postgres


def execute(data, pg: Postgres):

    # We delete our record from kino.movies first.
    # Due to foreign keys with 'on delete cascade', this clears all records from
    # the database associated with that imdb_id.
    imdb_id = data[0]['imdb_id']

    sql = """delete from kino.movies
              where imdb_id = '{0}'""".format(imdb_id)
    pg.pg_cur.execute(sql)
    pg.pg_conn.commit()

    sql = """insert into kino.errored(imdb_id, error_message)
             select x.imdb_id, x.error_message
               from json_to_recordset(%s) x (imdb_id varchar(1000), error_message varchar(4000))
                 on conflict (imdb_id)
                 do update
               set error_message = excluded.error_message
          """
    pg.pg_cur.execute(sql, (json.dumps(data),))
    pg.pg_conn.commit()

    return data