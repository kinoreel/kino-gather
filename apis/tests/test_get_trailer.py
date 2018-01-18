import unittest
import os
import sys
from mock import patch

current_dir = (os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(current_dir, '..', '..'))

from apis.get_trailer import GetAPI, RequestAPI, StandardisedResponse, ChooseBest, ValidateVideo


class TestGetAPI(unittest.TestCase):
    """Testing RequestAPI"""
    @classmethod
    def setUpClass(cls):
        cls.get = GetAPI()

    def test_retrieve_data(self):
        """Testing GetApi.retrieve_data"""

        request = {'imdb_id': 'tt0117509',
                   'tmdb_main': [{'title': 'Revolutionary Road', 'release_date': '2008-01-01'}],
                   'tmdb_trailer': [{'video_id': 'qADM67ZgYxM'}]}
        result = GetAPI.retrieve_data(request)
        expected = ('tt0117509', 'Revolutionary Road', 'qADM67ZgYxM', '2008-01-01', '2008')
        self.assertEqual(result, expected)

    def test_retrieve_data_no_trailer(self):
        """Testing GetApi.retrieve_data"""

        request = {'imdb_id': 'tt0117509',
                   'tmdb_main': [{'title': 'Revolutionary Road', 'release_date': '2008-01-01'}],
                   'tmdb_trailer': []}
        result = GetAPI.retrieve_data(request)
        expected = ('tt0117509', 'Revolutionary Road', None, '2008-01-01', '2008')
        self.assertEqual(result, expected)

    def test_get_tmdb_trailer_data_fail(self):
        a = GetAPI.get_tmdb_trailer_data('a')
        self.assertIsNone(a)

    def test_get_tmdb_trailer_data_pass(self):
        a = GetAPI.get_tmdb_trailer_data('qADM67ZgYxM')
        print(a)

    def test_get_info(self):
        """
        Top level test checking that we pull back the bes trailer for a film
        """
        request = {'imdb_id': 'tt0117509',
                   'tmdb_main': [{'title': 'Revolutionary Road', 'release_date': '2008-01-01'}]}
        result = self.get.get_info(request)
        expected = {
            'trailer_main': [{
                'imdb_id': 'tt0117509',
                'video_id': 'qADM67ZgYxM',
                'definition': 'hd',
                'channel_id': 'UC9YHyj7QSkkSg2pjQ7M8Khg',
                'channel_title': 'Paramount Movies'
            }]
        }
        self.assertEqual(result, expected)


class TestRequestAPI(unittest.TestCase):
    """Testing RequestAPI"""

    @classmethod
    def setUpClass(cls):
        cls.req = RequestAPI()

    # todo patch the youtube search functions
    def test_search_youtube_by_string(self):
        # Mock the request to the API
        # Blade Runner
        response = self.req.search_youtube_by_string('Revolutionary Road (2008) HD Trailer')
        print(response)

    # todo patch the youtube search functions
    def test_search_youtube_by_id(self):
        # Mock the request to the API
        # Blade Runner
        response = self.req.search_youtube_by_id('b1Stfe7Puk0')
        print(response)

    def test_get_trailers(self):
        response = self.req.get_trailers('Revolutionary Road', '2008')
        print(response)

    def test_get_tmdb_trailer(self):
        response = self.req.get_tmdb_trailer('1tTIQ8pkGf0')
        print(response)


class TestValidateVideo(unittest.TestCase):
    """Testing the class ValidateVideo"""

    def test_validate_pass(self):
        video = {'channelTitle': 'paramount picture', 'title': 'Trailer'}
        self.assertTrue(ValidateVideo.validate(video))

    def test_validate_fail_title(self):
        video = {'channelTitle': 'paramount picture', 'title': 'Deutsch Trailer'}
        self.assertFalse(ValidateVideo.validate(video))

    def test_validate_fail_channel(self):
        video = {'channelTitle': '7even3hreetv', 'title': 'Trailer'}
        self.assertFalse(ValidateVideo.validate(video))

    def test_validate_fail_region(self):
        video = {'channelTitle': '7even3hreetv', 'title': 'Trailer', 'regionRestriction': {'blocked': ['GB']}}
        self.assertFalse(ValidateVideo.validate(video))

    def test_check_region_fail(self):
        video = {'regionRestriction': {'blocked': ['GB']}}
        self.assertFalse(ValidateVideo.check_region(video))

    def test_check_region_pass(self):
        video = {}
        self.assertTrue(ValidateVideo.check_region(video))

    def test_check_title_fail(self):
        video = {'title': 'Deutsch Trailer'}
        self.assertFalse(ValidateVideo.check_title(video))

    def test_check_title_pass(self):
        video = {'title': 'Trailer'}
        self.assertTrue(ValidateVideo.check_title(video))

    def test_check_channel_fail(self):
        video = {'channelTitle': '7even3hreetv'}
        self.assertFalse(ValidateVideo.check_channel_title(video))

    def test_check_channel_pass(self):
        video = {'channelTitle': 'paramount picture'}
        self.assertTrue(ValidateVideo.check_channel_title(video))


class TestResponse(unittest.TestCase):
    """Testing the class StandardiseResponse"""

    @classmethod
    def setUpClass(cls):
        response = {
            'dislikeCount': '84',
            'likeCount': '2399',
            'channelId': 'UCgKkNPU2Ib7_TcyAl8M2S-w',
            'licensedContent': False,
            'viewCount': '686396',
            'video_id': 'iYhJ7Mf2Oxs',
            'projection': 'rectangular',
            'title': 'Blade Runner 30th Anniversary Trailer',
            'dimension': '2d',
            'liveBroadcastContent': 'none',
            'caption': 'false',
            'duration': 'PT2M29S',
            'favoriteCount': '0',
            'definition': 'sd',
            'channelTitle': 'Warner Bros. Home Entertainment',
            'publishedAt': '2012-09-07T02:08:05.000Z',
            'commentCount': '328'
        }
        cls.resp = StandardisedResponse('tt1234567', response)

    def test_get_main_data(self):
        result = self.resp.get_main_data()
        expected = {
            'viewCount': '686396',
            'title': 'Blade Runner 30th Anniversary Trailer',
            'channelTitle': 'Warner Bros. Home Entertainment',
            'channelId': 'UCgKkNPU2Ib7_TcyAl8M2S-w',
            'imdb_id': 'tt1234567',
            'publishedAt': '2012-09-07',
            'video_id': 'iYhJ7Mf2Oxs',
            'definition': 'sd'
        }
        self.assertEqual(expected, result)

    def test_get_def_score(self):
        result = self.resp.get_definition_score()
        self.assertEqual(result, 0)

class TestChooseBest(unittest.TestCase):
    """Testing the ChooseBest class"""

    def test_check_published_date(self):
        self.assertTrue(ChooseBest.check_published_date('2002-01-01', '2000-01-01'))
        self.assertFalse(ChooseBest.check_published_date('1997-01-01', '2000-01-01'))

    def test_check_title(self):
        self.assertTrue(ChooseBest.check_title('Awesome Film Trailer', 'Awesome Film'))
        self.assertFalse(ChooseBest.check_title('Awesome Film', 'Awesome Film'))
        self.assertFalse(ChooseBest.check_title('Awesome Trailer', 'Awesome Film'))

    def test_check_duration(self):
        self.assertTrue(ChooseBest.check_duration(1))
        self.assertFalse(ChooseBest.check_duration(6))

    def test_choose_best(self):
        data = [{
            # Was published too long ago, should be dropped
            'definition': 'hd',
            'imdb_id': 'tt1234567',
            'duration': 'PT3M15S',
            'publishedAt': '1990-01-01',
            'channelId': 'UCjmJDM5pRKbUlVIzDYYWb6g',
            'viewCount': '100',
            'video_id': '1',
            'channelTitle': 'TrailerChannel',
            'title': 'Awesome Movie - Official Trailer'
        }, {
            # Has bad duration
            'definition': 'hd',
            'imdb_id': 'tt1234567',
            'duration': 'PT13M15S',
            'publishedAt': '2005-01-01',
            'channelId': 'abcde',
            'viewCount': '100',
            'video_id': '2',
            'channelTitle': 'TrailerChannel',
            'title': 'Awesome Movie - Trailer'
        }, {
            # Has bad title
            'definition': 'hd',
            'imdb_id': 'tt1234567',
            'duration': 'PT3M15S',
            'publishedAt': '2005-01-01',
            'channelId': 'abcde',
            'viewCount': '100',
            'video_id': '3',
            'channelTitle': 'TrailerChannel',
            'title': 'Awesome - Trailer'
        }, {
            # SD trailer should be dropped
            'definition': 'sd',
            'imdb_id': 'tt1234567',
            'duration': 'PT3M15S',
            'publishedAt': '2005-01-01',
            'channelId': 'abcde',
            'viewCount': '100',
            'video_id': '4',
            'channelTitle': 'TrailerChannel',
            'title': 'Awesome Movie - Trailer'
        }, {
            # HD trailer, but low view count
            'definition': 'hd',
            'imdb_id': 'tt1234567',
            'duration': 'PT3M15S',
            'publishedAt': '2005-01-01',
            'channelId': 'abcde',
            'viewCount': '10',
            'video_id': '5',
            'channelTitle': 'TrailerChannel',
            'title': 'Awesome Movie - Trailer'
        }, {
            # HD trailer with high view count. Should be chosen
            'definition': 'hd',
            'imdb_id': 'tt1234567',
            'duration': 'PT3M15S',
            'publishedAt': '2005-01-01',
            'channelId': 'abcde',
            'viewCount': '50',
            'video_id': '6',
            'channelTitle': 'TrailerChannel',
            'title': 'Awesome Movie - Trailer'
        }]
        # Create response classes from our responses
        responses = [StandardisedResponse('tt1234567', e) for e in data]
        result = ChooseBest().choose_best(responses, '2000-01-01', 'Awesome Movie')
        # Confirm the last response was chosen
        self.assertEqual(data[-1], result.main_data)






