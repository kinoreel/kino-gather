import os
import unittest

from apis.get_youtube import GetAPI, RequestAPI, ChooseBest, StandardiseResponse


class TestGetAPI(unittest.TestCase):
    """Testing RequestAPI"""
    @classmethod
    def setUpClass(cls):
        cls.get = GetAPI()


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
        cls.response = [{
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

    def test_get_main_data(self):
        main_data = self.stan.get_main_data(self.response[0])
        expected_result = {
            'dislikeCount': '55',
            'title': 'Blade Runner: The Final Cut Special Edition',
            'channelTitle': 'warnervoduk',
            'projection': 'rectangular',
            'caption': 'true',
            'dimension': '2d',
            'commentCount': '8',
            'definition': 'hd',
            'video_id': '59cQqLrdmK8',
            'regionRestriction': 'IE,GB',
            'description': "The one that started it all. Ridley Scott's Blade Runner is one of the most important science-fiction movies of the 20th Century. Its futuristic depiction of a ...",
            'duration': 117,
            'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
            'likeCount': '223',
            'favoriteCount': '0',
            'liveBroadcastContent': 'none',
            'publishedAt': '2013-07-19T04:02:19.000Z'
        }
        self.assertEqual(main_data, expected_result)

    def test_standardised(self):
        main_data = self.stan.standardise(self.response)
        expected_result = [{
            'dimension': '2d',
            'caption': 'true',
            'video_id': '59cQqLrdmK8',
            'projection': 'rectangular',
            'commentCount': '8',
            'publishedAt': '2013-07-19T04:02:19.000Z',
            'title': 'Blade Runner: The Final Cut Special Edition',
            'dislikeCount': '55',
            'duration': 117,
            'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
            'regionRestriction': 'IE,GB',
            'channelTitle': 'warnervoduk',
            'favoriteCount': '0',
            'liveBroadcastContent': 'none',
            'description': "The one that started it all. Ridley Scott's Blade Runner is one of the most important science-fiction movies of the 20th Century. Its futuristic depiction of a ...",
            'likeCount': '223',
            'definition': 'hd'
        }, {
            'dimension': '2d',
            'caption': 'true',
            'video_id': 'rJ-T1ddFVRw',
            'projection': 'rectangular',
            'liveBroadcastContent': 'none',
            'publishedAt': '2014-01-20T09:56:51.000Z',
            'title': 'Blade Runner',
            'dislikeCount': '25',
            'duration': 117,
            'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
            'regionRestriction': 'GB,IE',
            'channelTitle': 'warnervoduk',
            'favoriteCount': '0',
            'description': '21st-century detective Rick Deckard brings his masculine-yet-vulnerable presence to this stylish noir thriller. In a future of high-tech possibility soured by urban ...',
            'likeCount': '43',
            'definition': 'hd'
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
        score = self.cb.get_match_score('Jaws', 124, 'Jaws 2', 116 )
        self.assertEqual(score, 72)

    def test_get_best_match(self):
        """
        We request a number of films from the YouTube API using the RequestAPI class.
        We then run the function  function and compare the result
        :return:
        """
        title = 'Blade Runner'
        runtime = '117'
        data = self.req.get_youtube(title)
        best_film = self.cb.get_best_match(data,title, runtime)
        self.assertEqual(best_film['youtube_films_main']['title'], 'Trainspotting')

        request = {'omdb_main': [{'title': 'El Club', 'runtime': '98'}],
                   'imdb_id': 'tt4375438'
                   }

        best_film = self.req.get_youtube(request)
        self.assertEqual(best_film['youtube_films_main'], {})

        request = {'omdb_main': [{'title': 'Planet of the Apes', 'runtime': '112'}],
                   'imdb_id': 'tt0063442'
                   }

        best_film = self.req.get_youtube(request)
        self.assertEqual(best_film['youtube_films_main']['title'], 'Planet of the Apes')


if __name__ == '__main__':
    unittest.main()
