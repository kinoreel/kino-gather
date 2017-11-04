import unittest

from apis.get_itunes import RequestAPI, Standardise, GetAPI, ChooseBest


class TestGetAPI(unittest.TestCase):
    """Testing RequestAPI"""
    @classmethod
    def setUpClass(cls):
        cls.get = GetAPI()

    def test_get_info(self):
        """
        An integration test checking that we pull back the expected film.
        """
        request = {'imdb_id': 'tt0083658',
                   'omdb_main': [{'title': 'Blade Runner'}],
                   'tmdb_main': [{'runtime': 117, 'release_date': '1982-06-25'}]}
        info = self.get.get_info(request)
        expected_result = {
            'itunes_main': {
                'released': '1982-09-09',
                'purchase_price': 7.99,
                'rental_price': 3.49,
                'hd_purchase_price': 7.99,
                'title': 'Blade Runner',
                'hd_rental_price': 3.49,
                'imdb_id': 'tt0083658',
                'url': 'https://itunes.apple.com/gb/movie/blade-runner/id594314564'
            }
        }
        self.assertEqual(expected_result, info)

class TestRequestAPI(unittest.TestCase):
    """Testing GetAPI"""
    @classmethod
    def setUpClass(cls):
        cls.get = RequestAPI()

    def test_get_info(self):
        # Check get_info for a correct imdb_id
        result = self.get.get_itunes('Blade Runner')

class TestStandardise(unittest.TestCase):
    """Testing StardardiseResponse"""

    @classmethod
    def setUpClass(cls):
        cls.stan = Standardise()
        cls.response = [{
            'shortDescription': '21st-century detective Rick Deckard brings his masculine-yet-vulnerable presence to this stylish',
            'artworkUrl60': 'http://is1.mzstatic.com/image/thumb/Video69/v4/1a/50/0e/1a500e1b-4f14-1260-77f6-a7d971ca58ab/source/60x60bb.jpg',
            'trackId': 594314564,
            'trackViewUrl': 'https://itunes.apple.com/gb/movie/blade-runner/id594314564?uo=4',
            'collectionHdPrice': 7.99,
            'longDescription': '21st-century detective Rick Deckard brings his masculine-yet-vulnerable presence to this stylish noir thriller. In a future of high-tech possibility soured by urban and social decay, Deckard hunts for fugitive, murderous replicants - and is drawn to a mystery woman whose secrets may undermine his soul.',
            'trackExplicitness': 'notExplicit',
            'trackName': 'Blade Runner',
            'trackHdPrice': 7.99,
            'artworkUrl100': 'http://is1.mzstatic.com/image/thumb/Video69/v4/1a/50/0e/1a500e1b-4f14-1260-77f6-a7d971ca58ab/source/100x100bb.jpg',
            'previewUrl': 'http://video.itunes.apple.com/apple-assets-us-std-000001/Video/v4/42/35/bf/4235bf7f-60ce-7056-bd5b-06c409ee6731/mzvf_7920601143535253426.640x360.h264lc.D2.p.m4v',
            'collectionExplicitness': 'notExplicit',
            'trackTimeMillis': 7029632,
            'wrapperType': 'track',
            'country': 'GBR',
            'trackRentalPrice': 3.49,
            'trackCensoredName': 'Blade Runner',
            'trackPrice': 6.99,
            'trackHdRentalPrice': 3.49,
            'collectionPrice': 6.99,
            'contentAdvisoryRating': '15',
            'kind': 'feature-movie',
            'primaryGenreName': 'Action & Adventure',
            'currency': 'GBP',
            'artworkUrl30': 'http://is1.mzstatic.com/image/thumb/Video69/v4/1a/50/0e/1a500e1b-4f14-1260-77f6-a7d971ca58ab/source/30x30bb.jpg',
            'releaseDate': '1982-09-09T07:00:00Z',
            'artistName': 'Ridley Scott'
        }, {
            'artworkUrl100': 'http://is3.mzstatic.com/image/thumb/Video128/v4/0c/45/e7/0c45e71a-460d-1d23-3d31-6c41c2cc1fb9/source/100x100bb.jpg',
            'releaseDate': '2017-10-04T07:00:00Z',
            'shortDescription': 'Thirty years after the events of the first film, a new blade runner, LAPD Officer K (Ryan Gosling),',
            'collectionExplicitness': 'notExplicit',
            'primaryGenreName': 'Sci-Fi & Fantasy',
            'wrapperType': 'track',
            'country': 'GBR',
            'trackCensoredName': 'Blade Runner 2049',
            'trackExplicitness': 'notExplicit',
            'trackId': 1287369934,
            'trackViewUrl': 'https://itunes.apple.com/gb/movie/blade-runner-2049/id1287369934?uo=4',
            'contentAdvisoryRating': '15',
            'kind': 'feature-movie',
            'trackName': 'Blade Runner 2049',
            'artworkUrl60': 'http://is3.mzstatic.com/image/thumb/Video128/v4/0c/45/e7/0c45e71a-460d-1d23-3d31-6c41c2cc1fb9/source/60x60bb.jpg',
            'currency': 'GBP',
            'longDescription': "Thirty years after the events of the first film, a new blade runner, LAPD Officer K (Ryan Gosling), unearths a long-buried secret that has the potential to plunge what's left of society into chaos. K's discovery leads him on a quest to find Rick Deckard (Harrison Ford), a former LAPD blade runner who has been missing for 30 years.",
            'artworkUrl30': 'http://is3.mzstatic.com/image/thumb/Video128/v4/0c/45/e7/0c45e71a-460d-1d23-3d31-6c41c2cc1fb9/source/30x30bb.jpg',
            'artistName': 'Denis Villeneuve'
        }]

    def test_standardised(self):
        standardised_data = self.stan.standardise('tt0083658', self.response)
        expected_result = [{
            'title': 'Blade Runner',
            'url': 'https://itunes.apple.com/gb/movie/blade-runner/id594314564',
            'released': '1982-09-09',
            'imdb_id': 'tt0083658',
            'purchase_price': 6.99,
            'hd_purchase_price': 7.99,
            'hd_rental_price': 3.49,
            'rental_price': 3.49
        }, {
            'title': 'Blade Runner 2049',
            'url': 'https://itunes.apple.com/gb/movie/blade-runner-2049/id1287369934',
            'released': '2017-10-04',
            'imdb_id': 'tt0083658',
            'purchase_price': None,
            'hd_purchase_price': None,
            'hd_rental_price': None,
            'rental_price': None
        }]
        self.assertEqual(standardised_data, expected_result)

    def test_get_main_data(self):
        """Testing get_main_data"""
        main_data = self.stan.get_main_data('tt0083658', self.response[0])
        expected_result = {
            'hd_purchase_price': 7.99,
            'imdb_id': 'tt0083658',
            'url': 'https://itunes.apple.com/gb/movie/blade-runner/id594314564',
            'title': 'Blade Runner',
            'purchase_price': 6.99,
            'released': '1982-09-09',
            'hd_rental_price': 3.49,
            'rental_price': 3.49
        }
        self.assertEqual(main_data, expected_result)

    def test_fix_release_date(self):
        """Testing fix_release_date"""
        release_date = self.stan.fix_release_date('1982-09-09T07:00:00Z')
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
        # todo probably add a few more test. Small, explicit examples.
        title = 'Blade Runner'
        release_date = '1982-06-25'
        data = [{
            'title': 'Blade Runner',
            'url': 'https://itunes.apple.com/gb/movie/blade-runner/id594314564',
            'released': '1982-09-09',
            'imdb_id': 'tt0083658',
            'purchase_price': 6.99,
            'hd_purchase_price': 7.99,
            'hd_rental_price': 3.49,
            'rental_price': 3.49
        }, {
            'title': 'Blade Runner 2049',
            'url': 'https://itunes.apple.com/gb/movie/blade-runner-2049/id1287369934',
            'released': '2017-10-04',
            'imdb_id': 'tt0083658',
            'purchase_price': None,
            'hd_purchase_price': None,
            'hd_rental_price': None,
            'rental_price': None
        }]
        best_film = self.cb.get_best_match(data, title, release_date)
        self.assertEqual(best_film['title'], title)
        self.assertEqual(best_film['url'], 'https://itunes.apple.com/gb/movie/blade-runner/id594314564')



if __name__ == '__main__':
    unittest.main()







if __name__=='__main__':
    unittest.main()
