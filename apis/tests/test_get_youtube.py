import sys
sys.path.append('..')

import unittest

from get_youtube import GetAPI, RequestAPI, ChooseBest, StandardiseResponse


class TestGetAPI(unittest.TestCase):
    """Testing RequestAPI"""
    @classmethod
    def setUpClass(cls):
        cls.get = GetAPI()

    def test_get_info(self):
        """
        An integration test checking that we pull back the expected film.
        """
        request = {'imdb_id': 'tt0117509',
                   'tmdb_main': [{'title': 'Romeo + Juliet', 'runtime': 120, 'release_date': '1997-03-28'}],
                   'itunes_main': [{'hq_rental_price': '1.99'}]}
        info = self.get.get_info(request)
        expected_result = {
            'youtube_main': [{
                'likeCount': '139',
                'favoriteCount': '0',
                'channelId': 'UCkE4NeJ68HT8mBkP97DG3Rg',
                'duration': '120',
                'dimension': '2d',
                'definition': 'sd',
                'imdb_id': 'tt0117509',
                'video_id': 'lOkJ-bV_la0',
                'title': 'Romeo + Juliet',
                'publishedAt': '2013-07-24',
                'regionRestriction': 'GB,IE',
                'dislikeCount': '93',
                'channelTitle': 'FoxInternationalHEGB'
            }]
        }
        self.maxDiff = None
        self.assertEqual(info, expected_result)

class TestRequestAPI(unittest.TestCase):
    """Testing RequestAPI"""

    @classmethod
    def setUpClass(cls):
        cls.req = RequestAPI()

    def test_get_youtube(self):
        # Blade Runner
        title = 'Blade Runner'
        response = self.req.get_youtube(title)

    def test_search_youtube(self):
        # Blade Runner
        title = 'Blade Runner'
        response = self.req.search_youtube(title)

    def test_get_content_details(self):
        # Blade Runner
        video_id = '59cQqLrdmK8'
        response = self.req.get_content_details(video_id)

    def test_get_stats(self):
        # Blade Runner
        video_id = '59cQqLrdmK8'
        response = self.req.get_stats(video_id)

class TestStandardiseResponse(unittest.TestCase):
    """Testing the class StandardiseResponse"""

    @classmethod
    def setUpClass(cls):
        cls.stan = StandardiseResponse()

    def setUp(self):
        self.response = [{
            'commentCount': '8',
            'likeCount': '223',
            'definition': 'hd',
            'video_id': '59cQqLrdmK8',
            'projection': 'rectangular',
            'publishedAt': '2013-07-19T04:02:19.000Z',
            'licensedContent': True,
            'title': 'Blade Runner: The Final Cut Special Edition',
            'caption': 'true',
            'duration': 'PT1H57M29S',
            'channelTitle': 'warnervoduk',
            'regionRestriction': {
                'allowed': ['IE', 'GB']
            },
            'dislikeCount': '55',
            'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
            'dimension': '2d',
            'liveBroadcastContent': 'none',
            'description': "The one that started it all. Ridley Scott's Blade Runner is one of the most important science-fiction movies of the 20th Century. Its futuristic depiction of a ...",
            'favoriteCount': '0'
        }, {
            'likeCount': '43',
            'definition': 'hd',
            'video_id': 'rJ-T1ddFVRw',
            'projection': 'rectangular',
            'publishedAt': '2014-01-20T09:56:51.000Z',
            'licensedContent': True,
            'title': 'Blade Runner',
            'caption': 'true',
            'duration': 'PT1H57M9S',
            'channelTitle': 'warnervoduk',
            'regionRestriction': {
                'allowed': ['GB', 'IE']
            },
            'dislikeCount': '25',
            'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
            'dimension': '2d',
            'liveBroadcastContent': 'none',
            'description': '21st-century detective Rick Deckard brings his masculine-yet-vulnerable presence to this stylish noir thriller. In a future of high-tech possibility soured by urban ...',
            'favoriteCount': '0'
        }]

    def test_fix_published_date(self):
        """Testing fix_published_date"""
        published_date = self.stan.fix_published_date('2013-07-19T04:02:19.000Z')
        self.assertEqual(published_date, '2013-07-19')

    def test_fix_runtime(self):
        """Testing fix_runtime"""
        runtime = self.stan.fix_runtime('PT1H41M19S')
        self.assertEqual(runtime, '101')

        runtime = self.stan.fix_runtime('PT41M19S')
        self.assertEqual(runtime, '41')

        runtime = self.stan.fix_runtime('PT1H19S')
        self.assertEqual(runtime, '60')

    def test_fix_title(self):
        """Testing fix_title"""
        title = self.stan.fix_title('Test movie (2016)')
        self.assertEqual(title, 'Test movie')

        title = self.stan.fix_title('Test movie (Subbed)')
        self.assertEqual(title, 'Test movie')

        title = self.stan.fix_title('1984')
        self.assertEqual(title, '1984')


    def test_get_main_data(self):
        main_data = self.stan.get_main_data('tt0083658', self.response[0])
        expected_result = {
            'favoriteCount': '0',
            'regionRestriction': 'GB,IE',
            'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
            'video_id': '59cQqLrdmK8',
            'likeCount': '223',
            'title': 'Blade Runner: The Final Cut Special Edition',
            'publishedAt': '2013-07-19',
            'imdb_id': 'tt0083658',
            'dimension': '2d',
            'definition': 'hd',
            'dislikeCount': '55',
            'duration': '117',
            'channelTitle': 'warnervoduk'
        }
        self.assertEqual(main_data, expected_result)

    def test_standardised(self):
        main_data = self.stan.standardise('tt0083658', self.response)
        expected_result = [{
            'definition': 'hd',
            'duration': '117',
            'channelTitle': 'warnervoduk',
            'imdb_id': 'tt0083658',
            'title': 'Blade Runner: The Final Cut Special Edition',
            'publishedAt': '2013-07-19',
            'dimension': '2d',
            'likeCount': '223',
            'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
            'regionRestriction': 'GB,IE',
            'dislikeCount': '55',
            'video_id': '59cQqLrdmK8',
            'favoriteCount': '0'
        }, {
            'definition': 'hd',
            'duration': '117',
            'channelTitle': 'warnervoduk',
            'imdb_id': 'tt0083658',
            'title': 'Blade Runner',
            'publishedAt': '2014-01-20',
            'dimension': '2d',
            'likeCount': '43',
            'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
            'regionRestriction': 'GB,IE',
            'dislikeCount': '25',
            'video_id': 'rJ-T1ddFVRw',
            'favoriteCount': '0'
        }]
        self.assertEqual(main_data, expected_result)


class TestChooseBest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cb = ChooseBest()
        cls.req = RequestAPI()

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

    def test_get_runtime_score(self):
        score = self.cb.get_runtime_score(100, 200)
        self.assertEqual(score, 100)
        score = self.cb.get_runtime_score(200, 100)
        self.assertEqual(score, 100)

    def test_get_match_score(self):
        score = self.cb.get_match_score('Blade Runner', 117, 'Blade Runner', 117)
        self.assertEqual(score, 100)
        score = self.cb.get_match_score('Blade Runner', 117, 'Blade Runner 2049', 164)
        self.assertEqual(score, 36)
        score = self.cb.get_match_score('Jaws', 124, 'Jaws 2', 116)
        self.assertEqual(score, 72)

    def test_get_release_date_score(self):
        """Testing get_release_date"""
        # Upload date sooner than release date is a good score
        # return 0
        score = self.cb.get_release_date_score('2016-07-03', '2016-02-19')
        self.assertEqual(score, 0)

        score = self.cb.get_release_date_score('2016-01-01', '2017-01-11')
        self.assertEqual(score, -13)

    def test_get_best_match(self):
        """
        We request a number of films from the YouTube API using the RequestAPI class.
        We then run the function  function and compare the result.
        """
        # todo probably add a few more test. Small, explicit examples.
        title = 'Blade Runner'
        runtime = 117
        release_date = '1982-06-25'
        data = [{
            'publishedAt': '2013-07-19',
            'definition': 'hd',
            'likeCount': '225',
            'duration': '113',
            'commentCount': '8',
            'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
            'dimension': '2d',
            'favoriteCount': '0',
            'caption': 'true',
            'channelTitle': 'warnervoduk',
            'title': 'Blade Runner: The Final Cut Special Edition',
            'dislikeCount': '56'
        }, {
            'publishedAt': '2014-01-20',
            'definition': 'hd',
            'likeCount': '43',
            'duration': '113',
            'commentCount': '0',
            'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
            'dimension': '2d',
            'favoriteCount': '0',
            'caption': 'true',
            'channelTitle': 'warnervoduk',
            'title': 'Blade Runner',
            'video_id': 'rJ-T1ddFVRw',
            'dislikeCount': '25'
        }, {
            'publishedAt': '2012-11-08',
            'definition': 'hd',
            'likeCount': '243',
            'duration': '123',
            'commentCount': '0',
            'channelId': 'UCkE4NeJ68HT8mBkP97DG3Rg',
            'favoriteCount': '0',
            'caption': 'false',
            'video_id': 'IQNJC4gd2-Y',
            'channelTitle': 'FoxInternationalHEGB',
            'title': 'Prometheus',
            'dislikeCount': '104'
        }, {
            'publishedAt': '2017-07-31',
            'definition': 'sd',
            'likeCount': '1',
            'duration': '144',
            'commentCount': '0',
            'channelId': 'UCQh-UjCCOoJx514uYmpdRmw',
            'dimension': '2d',
            'favoriteCount': '0',
            'caption': 'false',
            'video_id': 'CYdE27d4ipA',
            'channelTitle': 'moviepartnershipuk',
            'title': 'Metropolis',
            'dislikeCount': '0'
        }]
        best_film = self.cb.get_best_match(data, title, runtime, release_date)
        self.assertEqual(best_film['title'], title)
        self.assertEqual(best_film['video_id'], 'rJ-T1ddFVRw')


if __name__ == '__main__':
    unittest.main()
