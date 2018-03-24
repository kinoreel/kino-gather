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
        self.destination_topic = 'movies2streams'

    def run(self, data):
        """
        This inserts the relevant json information
        into the table kino.movies.
        :param data: json data holding information on films.
        """
        imdb_id = data['imdb_id']
        itunes_data = data['itunes_main']
        youtube_data = data['youtube_main']
        if youtube_data != []:

            sql = """
                insert into kino.movies2streams (imdb_id, source, url,  currency, price,  format, purchase_type, tstamp)
                select *
                  from ( select x.imdb_id
                              ,  unnest(array['GooglePlay', 'YouTube']) as source
                              ,  unnest(array['https://play.google.com/store/movies/details?id=' || x.video_id,
                                              'https://www.youtube.com/watch?v=' || x.video_id]) as url
                              , '£' as currency
                              , 2.49 as price
                              , x.definition as format
                              , 'rental' as purchase_type
                              , CURRENT_DATE
                           from json_to_recordset(%s) x (imdb_id varchar(1000), video_id varchar(1000), definition varchar(1000))
                        )  as data
                    on conflict (imdb_id, source, format, purchase_type)
                    do update
                   set url = excluded.url
                  """
            self.pg.pg_cur.execute(sql, (json.dumps(youtube_data), ))
            self.pg.pg_conn.commit()

        else:
            sql = """
                delete from kino.movies2streams
                 where source in ('GooglePlay', 'YouTube') and imdb_id = '{0}'""".format(imdb_id)

            self.pg.pg_cur.execute(sql)
            self.pg.pg_conn.commit()

        if itunes_data != []:

            sql = """
                insert into kino.movies2streams (imdb_id, source, url, currency, price, format, purchase_type, tstamp)
                select *
                  from ( select imdb_id
                              , 'iTunes' as source
                              , url
                              , '£'
                              , unnest(array[rental_price, hd_rental_price, purchase_price, hd_purchase_price])
                              , unnest(array['sd', 'hd', 'sd', 'hd']) as format
                              , unnest(array['rental', 'rental', 'purchase', 'purchase']) as purchase_type
                              , CURRENT_DATE
                           from json_to_recordset(%s) x ( imdb_id varchar(1000), url varchar(1000), rental_price real
                                                        , hd_rental_price real, purchase_price real, hd_purchase_price real)
                       ) as y
                    on conflict (imdb_id, source, format, purchase_type)
                    do update
                   set url = excluded.url
                """
            self.pg.pg_cur.execute(sql, (json.dumps(itunes_data), ))
            self.pg.pg_conn.commit()

        else:

            sql = """
                delete from kino.movies2streams
                 where source = 'iTunes' and imdb_id = '{0}'""".format(imdb_id)

            self.pg.pg_cur.execute(sql, (json.dumps(youtube_data),))
            self.pg.pg_conn.commit()
