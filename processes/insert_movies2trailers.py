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
        self.destination_topic = 'movies2trailers'

    def run(self, data):
        """
        This inserts the relevant json information
        into the table kino.movies.
        :param data: json data holding information on films.
        """
        trailer_data = data['trailer_main']

        sql = """insert into kino.movies2trailers ( imdb_id, video_id, title,  channel_id, channel_title, definition
                                                  , duration,  published_at, view_count, like_count, dislike_count
                                                  , comment_count, tstamp)
                 select imdb_id
                      , video_id
                      , title
                      , channel_id
                      , channel_title
                      , definition
                      , duration
                      , published_at
                      , view_count
                      , like_count
                      , dislike_count
                      , comment_count
                      , CURRENT_DATE
                   from json_to_recordset( %s) x ( imdb_id varchar(1000)
                                                 , video_id varchar(100)
                                                 , title varchar(100)
                                                 , channel_id varchar(100)
                                                 , channel_title varchar(100)
                                                 , definition varchar(2)
                                                 , duration int
                                                 , published_at date
                                                 , view_count int
                                                 , like_count int
                                                 , dislike_count int
                                                 , comment_count int)
                     on conflict (imdb_id)
                     do update
                    set video_id = excluded.video_id
                      , title = excluded.title
                      , channel_id = excluded.channel_id
                      , channel_title = excluded.channel_title
                      , definition = excluded.definition
                      , duration = excluded.duration
                      , published_at = excluded.published_at
                      , view_count = excluded.view_count
                      , like_count = excluded.like_count
                      , dislike_count = excluded.dislike_count
                      , comment_count = excluded.comment_count"""

        self.pg.pg_cur.execute(sql, (json.dumps(trailer_data),))
        self.pg.pg_conn.commit()
