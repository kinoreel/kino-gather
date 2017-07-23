import json

try:
    from postgres import Postgres
except ImportError:
    from inserts.postgres import Postgres


class InsertData(object):

    def __init__(self, server, port, database, username, password):
        self.pg = Postgres(server, port, database, username, password)
        self.source_topic = 'movies'
        self.destination_topic = 'movies2streams'

    def insert(self, data):
        """
        This inserts the relevant json information
        into the table kino.movies.
        :param data: json data holding information on films.
        """

        itunes_data = [data['itunes_main'],]
        youtube_data = data['youtube_films_main']

        sql = """insert into kino.movies2streams (imdb_id, source, url, currency, price, format, purchase_type, tstamp)
                 select *
                   from (select x.imdb_id
                              ,  unnest(array['GooglePlay', 'YouTube']) as source
                              ,  unnest(array['https://play.google.com/store/movies/details?id=' || x.video_id,
                                              'https://www.youtube.com/watch?v=' || x.video_id]) as url
                              , null::text
                              , null::real
                              , x.definition as format
                              , 'rental' as purchase_type
                              , CURRENT_DATE
                           from json_to_recordset(%s) x (imdb_id varchar(1000), video_id varchar(1000), definition varchar(1000))
                          where imdb_id <> ''
                          union
                         select imdb_id
                              , 'iTunes' as source
                              , url
                              , '£'
                              , unnest(array[rental_price, hd_rental_price, purchase_price, hd_purchase_price])
                              , unnest(array['sd', 'hd', 'sd', 'hd']) as format
                              , unnest(array['rental', 'rental', 'purchase', 'purchase']) as purchase_type
                              , CURRENT_DATE
                           from json_to_recordset(%s) y ( imdb_id varchar(1000), url varchar(1000), rental_price real
                                                        , hd_rental_price real, purchase_price real, hd_purchase_price real)
                          where imdb_id <> '') foo
                  where (foo.imdb_id, foo.source, foo.url, foo.format, foo.purchase_type) not in (select imdb_id
                                                                                   , source
                                                                                   , url
                                                                                   , format
                                                                                   , purchase_type
                                                                                from kino.movies2streams)
                 """

        self.pg.pg_cur.execute(sql, (json.dumps(youtube_data), json.dumps(itunes_data)))
        self.pg.pg_conn.commit()
