import logging

from processes.config import Config
from processes.get_omdb import Omdb
from processes.get_tmdb import Tmdb
from processes.get_trailer import Youtube
from processes.insert_errored import execute as insert_errored
from processes.insert_movies import execute as insert_movies
from processes.insert_movies2companies import execute as insert_movies2companies
from processes.insert_movies2genres import execute as insert_movies2genres
from processes.insert_movies2keywords import execute as insert_movies2keywords
from processes.insert_movies2numbers import execute as insert_movies2numbers
from processes.insert_movies2persons import execute as insert_movies2persons
from processes.insert_movies2ratings import execute as insert_movies2ratings
from processes.insert_movies2trailers import execute as insert_movies2trailers
from processes.postgres import Postgres

logger = logging.getLogger(__name__)

config = Config.from_env()
omdb = Omdb(api_key=config.OMDB_API_KEY)
tmdb = Tmdb(api_key=config.TMDB_API_KEY)
yt = Youtube(api_key=config.YOUTUBE_API_KEY)

postgres = Postgres(config.DB_SERVER, config.DB_PORT, config.DB_DATABASE, config.DB_USER, config.DB_PASSWORD)


def get_film(imdb_id):
    try:
        logger.info('Getting.. %s', imdb_id)

        payload = {'imdb_id': imdb_id}
        response = omdb.run({'imdb_id': imdb_id})
        payload.update(response)

        response = tmdb.run(payload)
        if response['tmdb_main'][0]['runtime'] < 60:
            raise AttributeError(f"Runtime is too low - {response['tmdb_main']['runtime']}")

        payload.update(response)
        response = yt.run(payload)

        payload.update(response)
        insert_movies(payload, postgres)
        insert_movies2companies(payload, postgres)
        insert_movies2keywords(payload, postgres)
        insert_movies2numbers(payload, postgres)
        insert_movies2persons(payload, postgres)
        insert_movies2ratings(payload, postgres)
        insert_movies2genres(payload, postgres)
        insert_movies2trailers(payload, postgres)
        logger.info('Got.. %s', imdb_id)
        return payload
    except Exception as e:
        logger.info('Failed to get.. %s', imdb_id)
        err_msg = {
            'imdb_id': imdb_id,
            'error_message': str(e)
        }
        insert_errored([err_msg], postgres)
        return err_msg
