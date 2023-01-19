import traceback

from flask import Flask, jsonify
from flask_cors import CORS

from processes.get_amazon import Main as get_amazon
from processes.get_itunes import Main as get_itunes
from processes.get_omdb import Main as get_omdb
from processes.get_tmdb import Main as get_tmdb
from processes.get_trailer import Main as get_trailer
from processes.get_youtube import Main as get_youtube
from processes.insert_errored import Main as insert_errored
from processes.insert_movies import Main as insert_movies
from processes.insert_movies2companies import Main as insert_movies2companies
from processes.insert_movies2genres import Main as insert_movies2genres
from processes.insert_movies2keywords import Main as insert_movies2keywords
from processes.insert_movies2numbers import Main as insert_movies2numbers
from processes.insert_movies2persons import Main as insert_movies2persons
from processes.insert_movies2ratings import Main as insert_movies2ratings
from processes.insert_movies2streams import Main as insert_movies2streams
from processes.insert_movies2trailers import Main as insert_movies2trailers

app = Flask(__name__)
cors = CORS(app)


@app.route('/health/')
def health():
    return "healthy"


@app.route('/imdb_id/<imdb_id>/')
def get_api(imdb_id):
    imdb_id = imdb_id
    try:
        app.logger.info('Getting.. %s', imdb_id)

        payload = {'imdb_id': imdb_id}
        response = get_omdb().run({'imdb_id': imdb_id})
        try:
            rotten_tom_score = [e for e in response['omdb_ratings'] if e["source"] == "Rotten Tomatoes"][0]['value']
        except:
            raise AttributeError(f"Unable to find rotten tomatoes rating")
        if int(rotten_tom_score) < 50:
            raise AttributeError(f"Score is too low - Rotten Tomatoes: {rotten_tom_score}")

        try:
            imdb_score = [e for e in response['omdb_ratings'] if e["source"] == "imdb"][0]['value']
        except:
            raise AttributeError(f"Unable to find imdb rating")
        if float(imdb_score) < 5:
            raise AttributeError(f"Score is too low - IMDB: {imdb_score}")

        payload.update(response)
        response = get_tmdb().run(payload)
        if response['tmdb_main'][0]['runtime'] < 60:
            raise AttributeError(f"Runtime is too low - {response['tmdb_main']['runtime']}")

        payload.update(response)
        response = get_trailer().run(payload)

        payload.update(response)
        # response = get_itunes().run(payload)
        # payload.update(response)
        # response = get_amazon().run(payload)
        # payload.update(response)
        # response = get_youtube().run(payload)
        # payload.update(response)
        insert_movies().run(payload)
        insert_movies2companies().run(payload)
        insert_movies2keywords().run(payload)
        insert_movies2numbers().run(payload)
        insert_movies2persons().run(payload)
        insert_movies2ratings().run(payload)
        insert_movies2genres().run(payload)
        # insert_movies2streams().run(payload)
        insert_movies2trailers().run(payload)
        app.logger.info('Got.. %s', imdb_id)
        return payload
    except Exception as e:
        app.logger.info('Failed to get.. %s', imdb_id)

        err_msg = [{'imdb_id': imdb_id,
                    'error_message': '{0}: {1}'.format("api error", traceback.format_exc())}]
        insert_errored().run(err_msg)
        return jsonify(err_msg)


if __name__ == '__main__':
    app = app.run(host='0.0.0.0', port=5000)
