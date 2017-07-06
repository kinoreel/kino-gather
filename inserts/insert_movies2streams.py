import json

from postgres import Postgres


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

        sources_data = data['guidebox_sources']
        prices_data = data['guidebox_prices']
        youtube_data = data['youtube_films_main']

        sql = """insert into movies_movies2streams (imdb_id, source, url, currency, price, format, purchase_type, tstamp)
                 select case when x.link is null and z.video_id is not null then
                           z.imdb_id
                        else
                           x.imdb_id
                        end
                      , case when x.link is null and z.video_id is not null then
                           'YouTube'
                        else
                           x.display_name
                        end
                      , case when x.link is null and z.video_id is not null then
                           'https://www.youtube.com/watch?v=' || z.video_id
                        else
                           x.link
                        end
                      , case when y.price is not null then '£' end as currency
                      , to_number(y.price, '99.9')
                      , y.format
                      , y.type
                      , CURRENT_DATE
                   from json_to_recordset(%s) x (imdb_id varchar(1000), display_name varchar(1000), source varchar(1000), link varchar(1000))
                   left join json_to_recordset(%s) y (imdb_id varchar(1000), source varchar(1000), price varchar(1000), format varchar(1000), type varchar(1000))
                     on x.imdb_id = y.imdb_id
                    and x.source = y.source
                   full join json_to_recordset(%s) z (imdb_id varchar(1000), definition varchar(1000), video_id varchar(1000))
                     on x.imdb_id = z.imdb_id
                    and x.source = 'youtube'
                    and x.link = 'https://www.youtube.com/watch?v=' || z.video_id
                  where (x.imdb_id, x.display_name, link) not in (select imdb_id
                                                                       , source
                                                                       , link
                                                                    from movies_movies2streams )"""

        self.pg.pg_cur.execute(sql, (json.dumps(sources_data), json.dumps(prices_data), json.dumps(youtube_data)))
        self.pg.pg_conn.commit()
