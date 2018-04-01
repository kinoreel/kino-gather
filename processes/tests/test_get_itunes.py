import unittest
import os
import sys
import responses

current_dir = (os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(current_dir, '..', '..'))

from processes.get_itunes import RequestAPI, iTunesFilm, Main, ChooseBest


class TestMain(unittest.TestCase):
    """Testing RequestAPI"""
    @classmethod
    def setUpClass(cls):
        cls.main = Main()

    @responses.activate
    def test_get_info(self):
        responses.add(responses.GET, 'http://itunes.apple.com/search',
                      json={'results': [{
                                'releaseDate': '1982-09-09T07:00:00Z',
                                'trackHdRentalPrice': 3.49,
                                'trackViewUrl': 'https://itunes.apple.com/gb/movie/blade-runner/id594314564?uo=4',
                                'collectionHdPrice': 7.99,
                                'trackRentalPrice': 3.49,
                                'collectionPrice': 7.99,
                                'trackPrice': 7.99,
                                'trackHdPrice': 7.99,
                                'trackName': 'Blade Runner',
                            }, {
                                'releaseDate': '2017-10-04T07:00:00Z',
                                'trackViewUrl': 'https://itunes.apple.com/gb/movie/blade-runner-2049/id1287369934?uo=4',
                                'currency': 'GBP',
                                'trackName': 'Blade Runner 2049',
                            }]
                            },
                      status=200)
        request = {'imdb_id': 'tt0083658',
                   'tmdb_main': [{'title': 'Blade Runner', 'runtime': 117, 'release_date': '1982-06-25'}]}
        result = self.main.run(request)
        expected = {
            'itunes_main': [{
                'title': 'Blade Runner',
                'imdb_id': 'tt0083658',
                'hd_purchase_price': 7.99,
                'released': '1982-09-09',
                'rental_price': 3.49,
                'hd_rental_price': 3.49,
                'purchase_price': 7.99,
                'url': 'https://itunes.apple.com/gb/movie/blade-runner/id594314564'
            }]
        }
        self.assertEqual(result, expected)

    @responses.activate
    def test_get_info_no_film(self):
        responses.add(responses.GET, 'http://itunes.apple.com/search',
                      json={'results': [{
                                'releaseDate': '2017-10-04T07:00:00Z',
                                'trackViewUrl': 'https://itunes.apple.com/gb/movie/blade-runner-2049/id1287369934?uo=4',
                                'currency': 'GBP',
                                'trackName': 'Blade Runner 2049',
                            }]
                            },
                      status=200)
        request = {'imdb_id': 'tt0083658',
                   'tmdb_main': [{'title': 'Blade Runner', 'runtime': 117, 'release_date': '1982-06-25'}]}
        result = self.main.run(request)
        expected = {'itunes_main': []}
        self.assertEqual(result, expected)


class TestRequestAPI(unittest.TestCase):
    """Testing GetAPI"""
    @classmethod
    def setUpClass(cls):
        cls.get = RequestAPI()

    @responses.activate
    def test_get_info(self):
        # Mock the request to the API
        responses.add(responses.GET, 'http://itunes.apple.com/search',
                      json={'results': [{'trackName': 'Blade Runner'}]},
                      status=200)
        result = self.get.get_itunes('Blade Runner')
        expected = [{'trackName': 'Blade Runner'}]
        self.assertEqual(result, expected)


class TestiTunesFilm(unittest.TestCase):
    """Testing StardardiseResponse"""

    @classmethod
    def setUpClass(cls):
        cls.response = {
            'trackId': 594314564,
            'trackViewUrl': 'https://itunes.apple.com/gb/movie/blade-runner/id594314564?uo=4',
            'collectionHdPrice': 7.99,
            'trackName': 'Blade Runner',
            'trackHdPrice': 7.99,
            'country': 'GBR',
            'trackRentalPrice': 3.49,
            'trackPrice': 6.99,
            'trackHdRentalPrice': 3.49,
            'collectionPrice': 6.99,
            'currency': 'GBP',
            'releaseDate': '1982-09-09T07:00:00Z',
            'artistName': 'Ridley Scott'
        }

    def test_iTunesVideo(self):
        film = iTunesFilm('tt0083658', self.response)
        result = film.main_data
        expected = {
            'hd_purchase_price': 7.99,
            'title': 'Blade Runner',
            'url': 'https://itunes.apple.com/gb/movie/blade-runner/id594314564',
            'hd_rental_price': 3.49,
            'rental_price': 3.49,
            'released': '1982-09-09',
            'purchase_price': 6.99,
            'imdb_id': 'tt0083658'
        }
        self.assertEqual(result, expected)

    def test_fix_release_date(self):
        """Testing fix_release_date"""
        release_date = iTunesFilm.fix_release_date('1982-09-09T07:00:00Z')
        self.assertEqual(release_date, '1982-09-09')


    def test_fix_title(self):
        """Testing fix_title"""
        result = iTunesFilm.fix_title('Hello World (2017)')
        self.assertEqual(result, 'Hello World')

        result = iTunesFilm.fix_title('Hello World (1918)')
        self.assertEqual(result, 'Hello World')

        result = iTunesFilm.fix_title('Hello (2017) World')
        self.assertEqual(result, 'Hello (2017) World')

        result = iTunesFilm.fix_title('Hello World 2017')
        self.assertEqual(result, 'Hello World 2017')

        result = iTunesFilm.fix_title('Hello World (2300)')
        self.assertEqual(result, 'Hello World (2300)')




def test_fix_release_date(self):
    """Testing fix_release_date"""
    release_date = iTunesFilm.fix_release_date('1982-09-09T07:00:00Z')
    self.assertEqual(release_date, '1982-09-09')

class TestChooseBest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cb = ChooseBest()
        cls.req = RequestAPI()

    def test_release_date_score(self):
        """Testing check_published_date"""
        score = self.cb.release_date_score('2010-01-01', '2011-01-01')
        self.assertEqual(score, 12.17)
        score = self.cb.release_date_score('2011-01-01', '2010-01-01')
        self.assertEqual(score, 12.17)
        score = self.cb.release_date_score('2011-01-01', '2011-01-01')
        self.assertEqual(score, 0)

    def test_get_title_score(self):
        score = self.cb.get_title_score('Blade Runner', 'Blade Runner')
        self.assertEqual(score, 100)
        score = self.cb.get_title_score('Blade Runner', 'BLADE RUNNER')
        self.assertEqual(score, 100)
        score = self.cb.get_title_score('Blade Runner', 'Blade Runner 2049')
        self.assertEqual(score, 83)
        score = self.cb.get_title_score('Jaws', 'Jaws 2')
        self.assertEqual(score, 80)
        score = self.cb.get_title_score("Bill and Ted's Excellent Adventure", "Bill and Ted's Bogus Journey")
        self.assertEqual(score, 61)

    def test_get_match_score(self):
        score = self.cb.get_match_score('Blade Runner', '1982-09-09', 'Blade Runner', '1982-09-09')
        self.assertEqual(score, 100)
        score = self.cb.get_match_score('Blade Runner', '1982-09-09', 'Blade Runner 2049', '2017-10-04')
        self.assertEqual(score, -343.97)
        score = self.cb.get_match_score('Jaws', '1975-12-26', 'Jaws 2', '1978-06-16')
        self.assertEqual(score, 49.9)

    def test_get_best_match(self):
        """
        We request a number of films from the YouTube API using the RequestAPI class.
        We then run the function  function and compare the result.
        """
        title = 'Blade Runner'
        release_date = '1982-06-25'
        response = [{
            'trackHdPrice': 7.99,
            'trackPrice': 7.99,
            'trackName': 'Blade Runner (The Final Cut)',
            'trackRentalPrice': 3.49,
            'currency': 'GBP',
            'trackViewUrl': 'https://itunes.apple.com/gb/movie/blade-runner-the-final-cut/id566651076?uo=4',
            'collectionHdPrice': 7.99,
            'collectionPrice': 7.99,
            'releaseDate': '2007-10-05T07:00:00Z',
            'trackHdRentalPrice': 3.49,
        }, {
            'trackHdPrice': 7.99,
            'trackPrice': 8.99,
            'trackName': "Blade Runner (Director's Cut)",
            'trackViewUrl': 'https://itunes.apple.com/gb/movie/blade-runner-directors-cut/id273857038?uo=4',
            'collectionHdPrice': 7.99,
            'collectionPrice': 8.99,
            'releaseDate': '1982-06-25T07:00:00Z',
        }, {
            'trackHdPrice': 7.99,
            'trackPrice': 7.99,
            'trackName': 'Blade Runner',
            'trackRentalPrice': 3.49,
            'trackHdRentalPrice': 3.49,
            'collectionHdPrice': 7.99,
            'collectionPrice': 7.99,
            'releaseDate': '1982-09-09T07:00:00Z',
            'trackViewUrl': 'https://itunes.apple.com/gb/movie/blade-runner/id594314564?uo=4',
        }, {
            'trackViewUrl': 'https://itunes.apple.com/gb/movie/blade-runner-2049/id1287369934?uo=4',
            'trackName': 'Blade Runner 2049',
            'releaseDate': '2017-10-04T07:00:00Z',
        }]
        films = [iTunesFilm('tt0083658', e) for e in response]
        best_film = self.cb.get_best_match(films, title, release_date)
        self.assertEqual(best_film.main_data['title'], title)
        self.assertEqual(best_film.main_data['url'], 'https://itunes.apple.com/gb/movie/blade-runner/id594314564')


if __name__ == '__main__':
    unittest.main()
