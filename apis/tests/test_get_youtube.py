import os
import unittest

from apis.get_youtube import GetAPI

try:
    YOUTUBE_FILMS_API = os.environ['API_KEY']
except KeyError:
    try:
        import GLOBALS
    except ImportError:
        print("API is not known")
        exit()

class TestIGetAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api = GetAPI(GLOBALS.YOUTUBE_FILMS_API)

    def test_get_info(self):
        request = {'omdb_main': [{'title': 'Trainspotting', 'runtime': '94'}],
                   'imdb_id': 'tt0117951'
                   }
        best_film = self.api.get_info(request)
        self.assertEqual(best_film['youtube_films_main']['title'], 'Trainspotting')

        request = {'omdb_main': [{'title': 'El Club', 'runtime': '98'}],
                   'imdb_id': 'tt4375438'
                   }

        best_film = self.api.get_info(request)
        self.assertEqual(best_film['youtube_films_main'], {})

        request = {'omdb_main': [{'title': 'Planet of the Apes', 'runtime': '112'}],
                   'imdb_id': 'tt0063442'
                   }

        best_film = self.api.get_info(request)
        print(best_film)
        self.assertEqual(best_film['youtube_films_main']['title'], 'Planet of the Apes')


if __name__ == '__main__':
    unittest.main()
