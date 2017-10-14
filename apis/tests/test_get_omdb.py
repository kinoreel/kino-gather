import os
import unittest
from apis.get_omdb import GetAPI, RequestAPI, StandardiseResponse


class TestGetAPI(unittest.TestCase):
    """Testing GetAPI"""
    @classmethod
    def setUpClass(cls):
        cls.get = GetAPI()

    def test_get_info(self):
        # Check get_info for a correct imdb_id
        request = {'imdb_id':'tt0083658'}
        expected_keys= ['omdb_main', 'omdb_cast', 'omdb_ratings', 'omdb_crew']
        info = self.get.get_info(request)
        self.assertEqual(set(info.keys()), set(expected_keys))

        request = {'imdb_id':'X'}
        info = self.get.get_info(request)
        self.assertEqual(info, None)


class TestRequestAPI(unittest.TestCase):
    """Testing RequestAPI"""

    @classmethod
    def setUpClass(cls):
        cls.req = RequestAPI()

    def test_get_omdbapi_json(self):
        # Blade Runner
        imdb_id = 'tt0083658'
        response = self.req.get_omdb(imdb_id)
        self.assertEqual(response['Response'], 'True')
        self.assertEqual(response['Title'], 'Blade Runner')

        # Run Lola Run
        imdb_id = 'tt0130827'
        response = self.req.get_omdb(imdb_id)
        self.assertEqual(response['Response'], 'True')
        self.assertEqual(response['Title'], 'Run Lola Run')

        # True Grit - 1969
        # Testing that the release year is not appending for films
        # that have been remade.
        imdb_id = 'tt0065126'
        response = self.req.get_omdb(imdb_id)
        self.assertEqual(response['Response'], 'True')
        self.assertEqual(response['Title'], 'True Grit')


        # Bad imdb_id
        imdb_id = 'X'
        response = self.req.get_omdb(imdb_id)
        self.assertEqual(response['Response'], 'False')



class TestStandardiseResponse(unittest.TestCase):
    """Testing StardardiseResponse"""

    @classmethod
    def setUpClass(cls):
        cls.stan = StandardiseResponse()
        cls.imdb_id = 'tt0083658'
        # Response for Blade Runner from the OMDBAPI, edited to test additional functionality.
        # The edits have been highlighted.
        cls.response = {
            'Writer': 'Hampton Fancher (screenplay), David Webb Peoples (screenplay), Philip K. Dick (novel)',
            'Website': 'N/A',
            'Title': 'Blade Runner',
            'Runtime': '117 min',
            # Actual metascore replaced with 'N/A'
            'Metascore': 'N/A',
            'Language': 'English, German, Cantonese, Japanese, Hungarian, Arabic',
            'Response': 'True',
            'Director': 'Ridley Scott',
            'Actors': 'Harrison Ford, Rutger Hauer, Sean Young, Edward James Olmos',
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
            'Production': 'Warner Bros. Pictures',
            'Rated': 'R',
            'Poster': 'https://images-na.ssl-images-amazon.com/images/M/MV5BNzQzMzJhZTEtOWM4NS00MTdhLTg0YjgtMjM4MDRkZjUwZDBlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg',
            'DVD': '27 Aug 1997',
            'Plot': 'A blade runner must pursue and try to terminate four replicants who stole a ship in space and have returned to Earth to find their creator.',
            'imdbVotes': '522,827',
            'Genre': 'Sci-Fi, Thriller',
            'Awards': 'Nominated for 2 Oscars. Another 11 wins & 16 nominations.',
            'BoxOffice': 'N/A',
            'Year': '1982',
            'Type': 'movie',
            'imdbRating': '8.2',
            'imdbID': 'tt0083658',
            'Released': '25 Jun 1982',
            'Country': 'USA, Hong Kong, UK'
        }

    def test_get_main_data(self):
        expected_result = [{'title': 'Blade Runner', 'year': '1982', 'imdb_id': 'tt0083658',
                            'plot': 'A blade runner must pursue and try to terminate four replicants who stole a ship in space and have returned to Earth to find their creator.',
                            'language': 'English, German, Cantonese, Japanese, Hungarian, Arabic', 'rated': 'R',
                            'poster': 'https://images-na.ssl-images-amazon.com/images/M/MV5BNzQzMzJhZTEtOWM4NS00MTdhLTg0YjgtMjM4MDRkZjUwZDBlXkEyXkFqcGdeQXVyNjU0OTQ0OTY@._V1_SX300.jpg',
                            'country': 'USA, Hong Kong, UK', 'boxoffice': 'N/A', 'runtime': '117 min',
                            'production': 'Warner Bros. Pictures', 'released': '25 Jun 1982'}]
        main_data = self.stan.get_main_data(self.imdb_id, self.response)
        self.assertEqual(expected_result, main_data)

    def test_split_role_specification(self):
        name = 'Joe Blog (novel)'
        name, spec = self.stan.split_role_specification(name)
        self.assertEqual(name, 'Joe Blog')
        self.assertEqual(spec, '(novel)')

        name = 'Joe Blog'
        name, spec = self.stan.split_role_specification(name)
        self.assertEqual(name, 'Joe Blog')
        self.assertEqual(spec, None)

    def test_get_crew_data(self):
        expected_result = [{'imdb_id': 'tt0083658', 'name': 'Ridley Scott', 'role': 'director'},
                           {'imdb_id': 'tt0083658', 'name': 'Hampton Fancher', 'role': 'writer (screenplay)'},
                           {'imdb_id': 'tt0083658', 'name': 'David Webb Peoples', 'role': 'writer (screenplay)'},
                           {'imdb_id': 'tt0083658', 'name': 'Philip K. Dick', 'role': 'writer (novel)'}]
        crew_data = self.stan.get_crew_data(self.imdb_id, self.response)
        self.assertEqual(crew_data, expected_result)

    def test_get_cast_data(self):
        expected_result = [{'imdb_id': 'tt0083658', 'name': 'Harrison Ford', 'role': 'actor'},
                           {'imdb_id': 'tt0083658', 'name': 'Rutger Hauer', 'role': 'actor'},
                           {'imdb_id': 'tt0083658', 'name': 'Sean Young', 'role': 'actor'},
                           {'imdb_id': 'tt0083658', 'name': 'Edward James Olmos', 'role': 'actor'}]
        cast_data = self.stan.get_cast_data(self.imdb_id, self.response)
        self.assertEqual(cast_data, expected_result)

    def test_get_ratings_data(self):
        expected_result =[{'value': '8.2', 'source': 'imdb', 'imdb_id': 'tt0083658'},
                          {'value': '8.2/10', 'source': 'Internet Movie Database', 'imdb_id': 'tt0083658'},
                          {'value': '90%', 'source': 'Rotten Tomatoes', 'imdb_id': 'tt0083658'},
                          {'value': '89/100', 'source': 'Metacritic', 'imdb_id': 'tt0083658'}]
        rating_data = self.stan.get_ratings_data(self.imdb_id, self.response)
        self.assertEqual(rating_data, expected_result)


if __name__ == '__main__':
    unittest.main()
