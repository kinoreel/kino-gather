from flask import Flask, jsonify
from flask_cors import CORS

from processes.gather import get_film

app = Flask(__name__)
cors = CORS(app)


@app.route('/health/')
def health():
    return "healthy"


@app.route('/imdb_id/<imdb_id>/')
def get_api(imdb_id):
    app.logger.info('Getting.. %s', imdb_id)
    return jsonify(get_film(imdb_id))


if __name__ == '__main__':
    app = app.run(host='0.0.0.0', port=5000)
