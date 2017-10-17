import os
import unittest

from apis.get_youtube import GetAPI, RequestAPI, ChooseBest, StandardiseResponse


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

        self.assertEqual(info['video_id'], 'rJ-T1ddFVRw')
        self.assertEqual(info['imdb_id'], 'tt0083658')

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
        self.stan.fix_published_date('2013-07-19T04:02:19.000Z')

    def test_get_main_data(self):
        main_data = self.stan.get_main_data('tt0083658', self.response[0])
        expected_result = {
            'likeCount': '223',
            'regionRestriction': 'IE,GB',
            'caption': 'true',
            'title': 'Blade Runner: The Final Cut Special Edition',
            'dimension': '2d',
            'duration': '117',
            'imdb_id': 'tt0083658',
            'publishedAt': '2013-07-19',
            'video_id': '59cQqLrdmK8',
            'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
            'favoriteCount': '0',
            'liveBroadcastContent': 'none',
            'projection': 'rectangular',
            'definition': 'hd',
            'commentCount': '8',
            'description': "The one that started it all. Ridley Scott's Blade Runner is one of the most important science-fiction movies of the 20th Century. Its futuristic depiction of a ...",
            'licensedContent': True,
            'dislikeCount': '55',
            'channelTitle': 'warnervoduk'
        }
        self.assertEqual(main_data, expected_result)

    def test_standardised(self):
        main_data = self.stan.standardise('tt0083658', self.response)
        expected_result = [{
            'licensedContent': True,
            'channelTitle': 'warnervoduk',
            'caption': 'true',
            'description': "The one that started it all. Ridley Scott's Blade Runner is one of the most important science-fiction movies of the 20th Century. Its futuristic depiction of a ...",
            'regionRestriction': 'IE,GB',
            'favoriteCount': '0',
            'title': 'Blade Runner: The Final Cut Special Edition',
            'projection': 'rectangular',
            'publishedAt': '2013-07-19',
            'video_id': '59cQqLrdmK8',
            'duration': '117',
            'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
            'liveBroadcastContent': 'none',
            'dimension': '2d',
            'definition': 'hd',
            'dislikeCount': '55',
            'imdb_id': 'tt0083658',
            'likeCount': '223',
            'commentCount': '8'
        }, {
            'duration': '117',
            'channelTitle': 'warnervoduk',
            'caption': 'true',
            'description': '21st-century detective Rick Deckard brings his masculine-yet-vulnerable presence to this stylish noir thriller. In a future of high-tech possibility soured by urban ...',
            'regionRestriction': 'GB,IE',
            'favoriteCount': '0',
            'title': 'Blade Runner',
            'projection': 'rectangular',
            'publishedAt': '2014-01-20',
            'video_id': 'rJ-T1ddFVRw',
            'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
            'liveBroadcastContent': 'none',
            'dimension': '2d',
            'definition': 'hd',
            'dislikeCount': '25',
            'imdb_id': 'tt0083658',
            'licensedContent': True,
            'likeCount': '43'
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

    def test_check_published_date(self):
        """Testing check_published_date"""
        result = self.cb.check_published_date('2010-01-01', '2011-01-01')
        self.assertFalse(result)
        result = self.cb.check_published_date('2011-01-01', '2010-01-01')
        self.assertTrue(result)

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
