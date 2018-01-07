import json
import psycopg2

try:
    from postgres import Postgres
except ImportError:
    from inserts.postgres import Postgres

from inserts.GLOBALS import PG_SERVER, PG_PORT, PG_DB, PG_USERNAME, PG_PASSWORD

class InsertData(object):

    def __init__(self, server, port, database, username, password):
        self.pg = Postgres(server, port, database, username, password)
        self.source_topic = 'movies'
        self.destination_topic = 'movies2trailers'

    def insert(self, data):
        """
        This inserts the relevant json information
        into the table kino.movies.
        :param data: json data holding information on films.
        """
        youtube_trailer_data = data['trailer_main']

        sql = """insert into kino.movies2trailers2 (imdb_id, video_id, quality, channel_title, channel_id, tstamp)
                 select imdb_id
                      , video_id
                      , definition
                      , channel_title
                      , channel_id
                      , CURRENT_DATE
                   from json_to_recordset( %s) x (imdb_id varchar(1000), video_id varchar(100), definition varchar(2), channel_title varchar(100), channel_id varchar(100))
                     on conflict on constraint movies2trailers2_pkey
                     do nothing"""

        self.pg.pg_cur.execute(sql, (json.dumps(youtube_trailer_data),))
        self.pg.pg_conn.commit()

if __name__=='__main__':

    from apis.get_trailer import GetAPI as trailer
    from apis.get_tmdb import GetAPI as tmdb
    get = trailer()
    tmdb = tmdb()
    ins = InsertData(PG_SERVER, PG_PORT, PG_DB, '*', '*')

    dbconn = {'database': PG_DB,
              'user': '*',
              'password': '*',
              'host': PG_SERVER,
              'port': PG_PORT,
              }

    pg_conn = psycopg2.connect(**dbconn)
    pg_cur = pg_conn.cursor()
    sql = """select imdb_id
                  from ( select imdb_id
                           from trailer_quality
                          union
                         select imdb_id
                           from errored
                          where error_message = 'No trailer could be found from TMDB' ) as bad_trailers
                  where imdb_id not in ( select imdb_id
                                           from movies2trailers2 )
                        """
    imdb_ids = pg_cur.execute(sql)
    imdb_ids = [e[0] for e in pg_cur.fetchall()]
    for i in imdb_ids:
        try:
            request = {'imdb_id': i}
            data = tmdb.get_info(request)
            request.update(data)
            data = get.get_info(request)
            request.update(data)
            print(request['trailer_main'])
            ins.insert(request)
        except:
            pass


