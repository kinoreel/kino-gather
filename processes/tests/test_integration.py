import unittest

from processes.get_omdb import Main as get_omdb
from processes.get_tmdb import Main as get_tmdb
from processes.get_trailer import Main as get_trailer


class IntegrationTest(unittest.TestCase):

    def test(self):
        imdb_id = "tt5451118"
        payload = {'imdb_id': imdb_id}
        response = get_omdb().run({'imdb_id': imdb_id})
        payload.update(response)
        response = get_tmdb().run(payload)
        payload.update(response)
        response = get_trailer().run(payload)
        payload.update(response)
        print(payload)
