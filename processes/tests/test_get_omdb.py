import unittest
import os
import sys
import responses

current_dir = (os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(current_dir, '..', '..'))

from processes.get_omdb import Main, RequestAPI, StandardiseResponse, GatherException


class TestMain(unittest.TestCase):
    """Testing GetAPI"""
    @classmethod
    def setUpClass(cls):
        cls.main = Main()

    @responses.activate
    def test_get_info(self):
        # Mock the request to the API
        responses.add(responses.GET, 'http://www.omdbapi.com',
                      json={'Title': 'Blade Runner',
                            'Runtime': '117 min',
                            'Metascore': 'N/A',
                            'Language': 'English, German, Cantonese, Japanese, Hungarian, Arabic',
                            'Response': 'True',
                            'Ratings': [{
                                'Source': 'Internet Movie Database',
                                'Value': '8.2/10'
                            }, {
                                'Source': 'Rotten Tomatoes',
                                'Value': '90%'
                            }, {
                                'Source': 'Metacritic',
                                'Value': '89/100'
                            }],
                            'Rated': 'R',
                            'DVD': '27 Aug 1997',
                            'Plot': 'A blade runner must pursue and try to terminate four replicants who stole a '
                                    'ship in space and have returned to Earth to find their creator.',
                            'Genre': 'Sci-Fi, Thriller',
                            'Year': '1982',
                            'imdbRating': '8.2',
                            'imdbID': 'tt0083658',
                            'Country': 'USA, Hong Kong, UK'
                            }, status=200)
        # Check get_info for a correct imdb_id
        request = {'imdb_id': 'tt0083658'}
        result = self.main.run(request)
        expected = {
            'omdb_ratings': [{
                'source': 'imdb',
                'value': '8.2',
                'imdb_id': 'tt0083658'
            }, {
                'source': 'Internet Movie Database',
                'value': '8.2',
                'imdb_id': 'tt0083658'
            }, {
                'source': 'Rotten Tomatoes',
                'value': '90',
                'imdb_id': 'tt0083658'
            }, {
                'source': 'Metacritic',
                'value': '89',
                'imdb_id': 'tt0083658'
            }],
            'omdb_main': [{
                'imdb_id': 'tt0083658',
                'title': 'Blade Runner',
                'language': 'English, German, Cantonese, Japanese, Hungarian, Arabic',
                'plot': 'A blade runner must pursue and try to terminate four replicants who stole a ship in space '
                        'and have returned to Earth to find their creator.',
                'rated': 'R',
                'country': 'USA, Hong Kong, UK'
            }]
        }
        self.assertEqual(expected, result)


class TestRequestAPI(unittest.TestCase):
    """Testing RequestAPI"""

    @classmethod
    def setUpClass(cls):
        cls.req = RequestAPI()

    @responses.activate
    def test_get_omdb_good(self):
        # Mock the request to the API
        responses.add(responses.GET, 'http://www.omdbapi.com',
                      json={'Response': 'True', 'Title': 'Blade Runner'},
                      status=200)
        imdb_id = 'tt0083658'
        response = self.req.get_omdb(imdb_id)
        self.assertEqual(response['Response'], 'True')
        self.assertEqual(response['Title'], 'Blade Runner')

    @responses.activate
    def test_get_omdb_bad(self):
        # Mock the request to the API
        responses.add(responses.GET, 'http://www.omdbapi.com'.format('tt0083658', self.req.api_key),
                      json={'Response': 'False', 'Error': 'Incorrect IMDb ID.'},
                      status=200)
        # Blade Runner
        imdb_id = 'invalid'
        self.failUnlessRaises(GatherException, self.req.get_omdb, imdb_id)


class TestStandardiseResponse(unittest.TestCase):
    """Testing StardardiseResponse"""

    @classmethod
    def setUpClass(cls):
        cls.stan = StandardiseResponse()
        cls.imdb_id = 'tt0083658'
        # Mock response from OMDBAPI.
        cls.response = {
            'Title': 'Blade Runner',
            'Runtime': '117 min',
            'Metascore': 'N/A',
            'Language': 'English, German, Cantonese, Japanese, Hungarian, Arabic',
            'Response': 'True',
            'Ratings': [{
                'Source': 'Internet Movie Database',
                'Value': '8.2/10'
            }, {
                'Source': 'Rotten Tomatoes',
                'Value': '90%'
            }, {
                'Source': 'Metacritic',
                'Value': '89/100'
            }],
            'Rated': 'R',
            'DVD': '27 Aug 1997',
            'Plot': 'A blade runner must pursue and try to terminate four replicants who stole a ship in space and'
                    ' have returned to Earth to find their creator.',
            'Genre': 'Sci-Fi, Thriller',
            'Year': '1982',
            'imdbRating': '8.2',
            'imdbID': 'tt0083658',
            'Country': 'USA, Hong Kong, UK'
        }

    def test_get_main_data(self):
        expected_result = [{
            'plot': 'A blade runner must pursue and try to terminate four replicants who stole a ship in space and'
                    ' have returned to Earth to find their creator.',
            'language': 'English, German, Cantonese, Japanese, Hungarian, Arabic',
            'country': 'USA, Hong Kong, UK',
            'title': 'Blade Runner',
            'imdb_id': 'tt0083658',
            'rated': 'R'
        }]
        main_data = self.stan.get_main_data(self.imdb_id, self.response)
        self.assertEqual(expected_result, main_data)

    def test_get_ratings_data(self):
        expected_result = [{'value': '8.2', 'source': 'imdb', 'imdb_id': 'tt0083658'},
                           {'value': '8.2', 'source': 'Internet Movie Database', 'imdb_id': 'tt0083658'},
                           {'value': '90', 'source': 'Rotten Tomatoes', 'imdb_id': 'tt0083658'},
                           {'value': '89', 'source': 'Metacritic', 'imdb_id': 'tt0083658'}]
        rating_data = self.stan.get_ratings_data(self.imdb_id, self.response)
        self.assertEqual(rating_data, expected_result)


if __name__ == '__main__':
    unittest.main()
