import unittest
import os
import sys
from apiclient.http import HttpMock
from mock import patch

current_dir = (os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(current_dir, '..', '..'))

from processes.get_youtube import Main, RequestAPI, ChooseBest, YouTubeFilm, GatherException


class TestMain(unittest.TestCase):
    """Testing RequestAPI"""
    @classmethod
    def setUpClass(cls):
        cls.main = Main()

    # For the top level tests, we mock the RequestAPI class, rather
    # than mocking the GoogleAPI, because it is easier.
    @patch('processes.get_youtube.RequestAPI')
    def test_get_info(self, mock_request):
        """
        An integration test checking that we pull back the expected film.
        """
        request_instance = mock_request
        request_instance.return_value.get_youtube.return_value = [{
            'licensedContent': True,
            'favoriteCount': '0',
            'definition': 'hd',
            'projection': 'rectangular',
            'publishedAt': '2014-01-20T09:56:51.000Z',
            'description': '21st-century detective Rick Deckard brings his masculine-yet-vulnerable presence to '
                           'this stylish noir thriller. In a future of high-tech possibility soured by urban '
                           'and social decay, Deckard...',
            'regionRestriction': {
                'allowed': ['GB', 'IE']
            },
            'liveBroadcastContent': 'none',
            'dislikeCount': '97',
            'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
            'caption': 'true',
            'commentCount': '0',
            'likeCount': '321',
            'channelTitle': 'warnervoduk',
            'video_id': 'rJ-T1ddFVRw',
            'dimension': '2d',
            'duration': 'PT1H57M29S',
            'title': 'Blade Runner'
        }]

        request = {'imdb_id': 'tt0117509',
                   'tmdb_main': [{'title': 'Blade Runner', 'runtime': 117, 'release_date': '1982-06-25'}],
                   'itunes_main': [{'title': 'Blade Runner'}]}

        result = self.main.run(request)
        expected = {
            'youtube_main': [{
                'likeCount': '321',
                'duration': '117',
                'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
                'dimension': '2d',
                'regionRestriction': 'GB,IE',
                'imdb_id': 'tt0117509',
                'publishedAt': '2014-01-20',
                'dislikeCount': '97',
                'channelTitle': 'warnervoduk',
                'video_id': 'rJ-T1ddFVRw',
                'definition': 'hd',
                'title': 'Blade Runner',
                'favoriteCount': '0'
            }]
        }
        self.assertEqual(expected, result)

    @patch('processes.get_youtube.RequestAPI')
    def test_get_info_no_film(self, mock_request):
        """
        An integration test checking that we pull back the expected film.
        """
        request_instance = mock_request
        request_instance.return_value.get_youtube.return_value = [{
            'licensedContent': True,
            'favoriteCount': '0',
            'definition': 'sd',
            'projection': 'rectangular',
            'publishedAt': '2014-01-20T09:56:51.000Z',
            'description': 'A film that we definitely do not want on our application',
            'regionRestriction': {
                'allowed': ['GB', 'IE']
            },
            'liveBroadcastContent': 'none',
            'dislikeCount': '1000',
            'channelId': 'fh3pIdkvGBqao9UYNQP809PA',
            'caption': 'true',
            'commentCount': '0',
            'likeCount': '0',
            'channelTitle': 'badfilms',
            'video_id': 'ru9Io7dFVRw',
            'dimension': '1d',
            'duration': 'PT10H30M29S',
            'title': 'A really bad film'
        }]

        request = {'imdb_id': 'tt0117509',
                   'tmdb_main': [{'title': 'Blade Runner', 'runtime': 117, 'release_date': '1982-06-25'}],
                   'itunes_main': [{'title': 'Blade Runner'}]}

        result = self.main.run(request)
        expected = {'youtube_main': []}
        self.assertEqual(expected, result)

    @patch('processes.get_youtube.RequestAPI')
    def test_get_info_no_other_streams(self, mock_request):
        """
        An integration test checking that we pull back the expected film.
        """
        request_instance = mock_request
        request_instance.return_value.get_youtube.return_value = [{
            'licensedContent': True,
            'favoriteCount': '0',
            'definition': 'sd',
            'projection': 'rectangular',
            'publishedAt': '2014-01-20T09:56:51.000Z',
            'description': 'A film that we definitely do not want on our application',
            'regionRestriction': {
                'allowed': ['GB', 'IE']
            },
            'liveBroadcastContent': 'none',
            'dislikeCount': '1000',
            'channelId': 'fh3pIdkvGBqao9UYNQP809PA',
            'caption': 'true',
            'commentCount': '0',
            'likeCount': '0',
            'channelTitle': 'badfilms',
            'video_id': 'ru9Io7dFVRw',
            'dimension': '1d',
            'duration': 'PT10H30M29S',
            'title': 'A really bad film'
        }]

        request = {'imdb_id': 'tt0117509',
                   'tmdb_main': [{'title': 'Blade Runner', 'runtime': 117, 'release_date': '1982-06-25'}],
                   'itunes_main': []}

        self.failUnlessRaises(GatherException, self.main.run, request)


class TestRequestAPI(unittest.TestCase):
    """Testing RequestAPI"""

    @classmethod
    def setUpClass(cls):
        http = HttpMock('google-api-responses/youtube-discovery.json', {'status': '200'})
        api_key = 'API_KEY'
        cls.req = RequestAPI(api_key, http)

    def test_get_youtube(self):
        search_http = HttpMock('google-api-responses/youtube-films-search.json', {'status': '200'})
        content_details_http = HttpMock('google-api-responses/youtube-films-content_details.json', {'status': '200'})
        stats_http = HttpMock('google-api-responses/youtube-films-stats.json', {'status': '200'})
        result = self.req.get_youtube('blade runner', search_http, content_details_http, stats_http)
        expected = [{
            'licensedContent': True,
            'favoriteCount': '0',
            'definition': 'hd',
            'projection': 'rectangular',
            'publishedAt': '2014-01-20T09:56:51.000Z',
            'description': '21st-century detective Rick Deckard brings his masculine-yet-vulnerable presence to '
                           'this stylish noir thriller. In a future of high-tech possibility soured by urban '
                           'and social decay, Deckard...',
            'regionRestriction': {
                'allowed': ['GB', 'IE']
            },
            'liveBroadcastContent': 'none',
            'dislikeCount': '97',
            'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
            'caption': 'true',
            'commentCount': '0',
            'likeCount': '321',
            'channelTitle': 'warnervoduk',
            'video_id': 'rJ-T1ddFVRw',
            'dimension': '2d',
            'duration': 'PT1H57M29S',
            'title': 'Blade Runner'
        }, {
            'licensedContent': True,
            'favoriteCount': '0',
            'definition': 'hd',
            'projection': 'rectangular',
            'publishedAt': '2013-07-19T04:02:19.000Z',
            'description': "The one that started it all. Ridley Scott's Blade Runner is one of the most important "
                           "science-fiction movies of the 20th Century. Its futuristic depiction of a "
                           "post-apocalyptic, dystopian world...",
            'regionRestriction': {
                'allowed': ['GB', 'IE']
            },
            'liveBroadcastContent': 'none',
            'dislikeCount': '97',
            'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
            'caption': 'true',
            'commentCount': '0',
            'likeCount': '321',
            'channelTitle': 'warnervoduk',
            'video_id': '59cQqLrdmK8',
            'dimension': '2d',
            'duration': 'PT1H57M29S',
            'title': 'Blade Runner: The Final Cut Special Edition'
        }]
        self.assertEqual(result, expected)

    def test_search_youtube(self):
        http = HttpMock('google-api-responses/youtube-films-search.json', {'status': '200'})
        result = self.req.search_youtube('blade runner', http)
        expected = [{
            'etag': '"g7k5f8kvn67Bsl8L-Bum53neIr4/WAVFA12qvhEv3kGcmmq9qJwyRNk"',
            'id': {
                'kind': 'youtube#video',
                'videoId': 'rJ-T1ddFVRw'
            },
            'snippet': {
                'liveBroadcastContent': 'none',
                'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
                'channelTitle': 'warnervoduk',
                'description': '21st-century detective Rick Deckard brings his masculine-yet-vulnerable '
                               'presence to this stylish noir thriller. In a future of high-tech possibility '
                               'soured by urban and social decay, Deckard...',
                'publishedAt': '2014-01-20T09:56:51.000Z',
                'title': 'Blade Runner'
            },
            'kind': 'youtube#searchResult'
        }, {
            'etag': '"g7k5f8kvn67Bsl8L-Bum53neIr4/NWxfpBvtqNPc7OAaV63b5qs4IRM"',
            'id': {
                'kind': 'youtube#video',
                'videoId': '59cQqLrdmK8'
            },
            'snippet': {
                'liveBroadcastContent': 'none',
                'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
                'channelTitle': 'warnervoduk',
                'description': "The one that started it all. Ridley Scott's Blade Runner is one of the most important"
                               " science-fiction movies of the 20th Century. Its futuristic depiction of a "
                               "post-apocalyptic, dystopian world...",
                'publishedAt': '2013-07-19T04:02:19.000Z',
                'title': 'Blade Runner: The Final Cut Special Edition'
            },
            'kind': 'youtube#searchResult'
        }]
        self.assertEqual(result, expected)

    def test_get_content_details(self):
        http = HttpMock('google-api-responses/youtube-films-content_details.json', {'status': '200'})
        result = self.req.get_content_details('59cQqLrdmK8', http)
        expected = {
            'dimension': '2d',
            'regionRestriction': {
                'allowed': ['GB', 'IE']
            },
            'duration': 'PT1H57M29S',
            'definition': 'hd',
            'projection': 'rectangular',
            'licensedContent': True,
            'caption': 'true'
        }
        self.assertEqual(result, expected)

    def test_get_stats(self):
        http = HttpMock('google-api-responses/youtube-films-stats.json', {'status': '200'})
        result = self.req.get_stats('59cQqLrdmK8', http)
        expected = {
            'favoriteCount': '0',
            'commentCount': '0',
            'likeCount': '321',
            'dislikeCount': '97'
        }
        self.assertEqual(result, expected)


class TestYouTubeFilm(unittest.TestCase):
    """Testing the class YouTubeFilm"""

    def test_YouTubeFilm(self):
        response = {
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
            'description': "The one that started it all. Ridley Scott's Blade Runner is one of the most important"
                           " science-fiction movies of the 20th Century. Its futuristic depiction of a ...",
            'favoriteCount': '0'
        }
        result = YouTubeFilm('tt0083658', response)
        result = result.main_data
        expected = {
            'title': 'Blade Runner: The Final Cut Special Edition',
            'favoriteCount': '0',
            'regionRestriction': 'GB,IE',
            'imdb_id': 'tt0083658',
            'channelTitle': 'warnervoduk',
            'likeCount': '223',
            'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
            'dislikeCount': '55',
            'publishedAt': '2013-07-19',
            'video_id': '59cQqLrdmK8',
            'duration': '117',
            'dimension': '2d',
            'definition': 'hd'
        }
        self.assertEqual(result, expected)

    def test_fix_published_date(self):
        """Testing fix_published_date"""
        published_date = YouTubeFilm.fix_published_date('2013-07-19T04:02:19.000Z')
        self.assertEqual(published_date, '2013-07-19')

    def test_fix_runtime(self):
        """Testing fix_runtime"""
        runtime = YouTubeFilm.fix_runtime('PT1H41M19S')
        self.assertEqual(runtime, '101')

        runtime = YouTubeFilm.fix_runtime('PT41M19S')
        self.assertEqual(runtime, '41')

        runtime = YouTubeFilm.fix_runtime('PT1H19S')
        self.assertEqual(runtime, '60')

    def test_fix_title(self):
        """Testing fix_title"""
        title = YouTubeFilm.fix_title('Test movie (2016)')
        self.assertEqual(title, 'Test movie')

        title = YouTubeFilm.fix_title('Test movie (Subbed)')
        self.assertEqual(title, 'Test movie')

        title = YouTubeFilm.fix_title('1984')
        self.assertEqual(title, '1984')


class TestChooseBest(unittest.TestCase):

    def test_get_match_score(self):
        score = ChooseBest.get_match_score('Blade Runner', 117, '2016-07-03', 'Blade Runner', 117, '2016-02-19')
        self.assertEqual(score, 100)
        score = ChooseBest.get_match_score('Blade Runner', 117, '2016-07-03', 'Blade Runner 2049', 164, '2016-02-19')
        self.assertEqual(score, 36)
        score = ChooseBest.get_match_score('Jaws', 124, '2016-07-03', 'Jaws 2', 116, '2016-02-19')
        self.assertEqual(score, 72)

    def test_get_title_score(self):
        score = ChooseBest.get_title_score('Blade Runner', 'Blade Runner')
        self.assertEqual(score, 100)
        score = ChooseBest.get_title_score('Blade Runner', 'BLADE RUNNER')
        self.assertEqual(score, 100)
        score = ChooseBest.get_title_score('Blade Runner', 'Blade Runner 2049')
        self.assertEqual(score, 83)
        score = ChooseBest.get_title_score('Jaws', 'Jaws 2')
        self.assertEqual(score, 80)
        score = ChooseBest.get_title_score("Bill and Ted's Excellent Adventure", "Bill and Ted's Bogus Journey")
        self.assertEqual(score, 61)

    def test_get_runtime_score(self):
        score = ChooseBest.get_runtime_score(100, 200)
        self.assertEqual(score, 100)
        score = ChooseBest.get_runtime_score(200, 100)
        self.assertEqual(score, 100)

    def test_get_release_date_score(self):
        """Testing get_release_date"""
        # Upload date sooner than release date is a good score
        # return 0
        score = ChooseBest.get_release_date_score('2016-07-03', '2016-02-19')
        self.assertEqual(score, 0)

        score = ChooseBest.get_release_date_score('2016-01-01', '2017-01-11')
        self.assertEqual(score, 13)

    def test_get_best_match(self):
        """
        We request a number of films from the YouTube API using the RequestAPI class.
        We then run the function  function and compare the result.
        """
        title = 'Blade Runner'
        runtime = 117
        release_date = '1982-06-25'
        response = [{
            'publishedAt': '2013-07-19',
            'definition': 'hd',
            'likeCount': '225',
            'duration': 'PT1H53M19S',
            'commentCount': '8',
            'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
            'dimension': '2d',
            'favoriteCount': '0',
            'caption': 'true',
            'channelTitle': 'warnervoduk',
            'title': 'Blade Runner: The Final Cut Special Edition',
            'video_id': 'rJ-T1fg3htk',
            'dislikeCount': '56'
        }, {
            'publishedAt': '2014-01-20',
            'definition': 'hd',
            'likeCount': '43',
            'duration': 'PT1H53M19S',
            'commentCount': '0',
            'channelId': 'UCsDKdkvGBqaD-KINQP8WAEA',
            'favoriteCount': '0',
            'caption': 'true',
            'channelTitle': 'warnervoduk',
            'title': 'Blade Runner',
            'dimension': '2d',
            'video_id': 'rJ-T1ddFVRw',
            'dislikeCount': '25'
        }, {
            'publishedAt': '2012-11-08',
            'definition': 'hd',
            'likeCount': '243',
            'duration': 'PT2H03M19S',
            'commentCount': '0',
            'channelId': 'UCkE4NeJ68HT8mBkP97DG3Rg',
            'favoriteCount': '0',
            'caption': 'false',
            'dimension': '2d',
            'video_id': 'IQNJC4gd2-Y',
            'channelTitle': 'FoxInternationalHEGB',
            'title': 'Prometheus',
            'dislikeCount': '104'
        }, {
            'publishedAt': '2017-07-31',
            'definition': 'sd',
            'likeCount': '1',
            'duration': 'PT2H24M19S',
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
        films = [YouTubeFilm('tt0083658', e) for e in response]
        best_film = ChooseBest.get_best_match(films, title, runtime, release_date)
        self.assertEqual(best_film.main_data['title'], title)
        self.assertEqual(best_film.main_data['video_id'], 'rJ-T1ddFVRw')


if __name__ == '__main__':
    unittest.main()
