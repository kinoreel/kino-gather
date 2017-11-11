import unittest
import json

from apis.get_youtube import GetAPI as yt
from apis.get_omdb import GetAPI as omdb
from apis.get_tmdb import GetAPI as tmdb
from apis.get_itunes import GetAPI as itunes


class TestApis(unittest.TestCase):
    """Integration testing"""
    @classmethod
    def setUpClass(cls):
        cls.yt = yt()
        cls.omdb = omdb()
        cls.tmdb = tmdb()
        cls.itunes = itunes()

    def testAll(self):
        request = {'imdb_id': 'tt2562232'}
        data = self.omdb.get_info(request)
        request.update(data)
        data = self.tmdb.get_info(request)
        request.update(data)
        data = self.itunes.get_info(request)
        request.update(data)
        data = self.yt.get_info(request)
        request.update(data)
        print(json.dumps(request))


if __name__=='__main__':
    unittest.main()


