import unittest
import os
import sys
from mock import patch

current_dir = (os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(current_dir, '..', '..'))

from apis.get_trailer import GetAPI, YouTubeAPI, YouTubeVideo, ChooseBest, Validate


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
        a = GetAPI.get_tmdb_trailer_data('invalid')
        self.assertIsNone(a)

    def test_get_tmdb_trailer_data_none(self):
        a = GetAPI.get_tmdb_trailer_data('invalid')
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


class TestYouTubeAPI(unittest.TestCase):
    """Testing RequestAPI"""

    @classmethod
    def setUpClass(cls):
        cls.api = YouTubeAPI()

    # todo patch the youtube search functions
    def test_search_by_string(self):
        # Mock the request to the API
        # Blade Runner
        response = self.api.search_by_string('Revolutionary Road (2008) HD Trailer')
        print(response)

    # todo patch the youtube search functions
    def test_search_by_id(self):
        # Mock the request to the API
        # Blade Runner
        response = self.api.search_by_id('b1Stfe7Puk0')
        print(response)
        expected = {
            'publishedAt': '2016-03-29T09:42:39.000Z',
            'projection': 'rectangular',
            'caption': 'false',
            'channelId': 'UC_G61kX-ORlltt4b20_Oriw',
            'dislikeCount': '84',
            'tags': ['mr.chawaks'],
            'favoriteCount': '0',
            'categoryId': '10',
            'definition': 'sd',
            'title': 'Letta Mbulu - Nomalizo',
            'duration': 'PT5M11S',
            'dimension': '2d',
            'licensedContent': False,
            'description': '',
            'liveBroadcastContent': 'none',
            'viewCount': '448579',
            'channelTitle': 'Mr. Chawaks',
            'commentCount': '120',
            'likeCount': '6675'
        }


class TestValidate(unittest.TestCase):
    """Testing the class ValidateVideo"""

    def test_validate_pass(self):
        response = {'snippet': {'channelTitle': 'paramount picture', 'title': 'Trailer'}, 'duration': 'PT04M15S'}
        self.assertTrue(Validate.validate(response))

    def test_validate_fail_title(self):
        response = {'snippet': {'channelTitle': 'paramount picture', 'title': 'Deutsch Trailer'}, 'duration': 'PT04M15S'}
        self.assertFalse(Validate.validate(response))

    def test_validate_fail_channel(self):
        response = {'snippet': {'channelTitle': '7even3hreetv', 'title': 'Trailer'}, 'duration': 'PT04M15S'}
        self.assertFalse(Validate.validate(response))

    def test_validate_fail_duration(self):
        response = {'snippet': {'channelTitle': 'paramount picture', 'title': 'Trailer'}, 'duration': 'PT14M15S'}
        self.assertFalse(Validate.validate(response))

    def test_validate_fail_region(self):
        response = {'snippet': {'channelTitle': 'paramount picture', 'title': 'Trailer'}, 'duration': 'PT14M15S',
                    'regionRestriction': {'blocked': ['GB']}}
        self.assertFalse(Validate.validate(response))

    def test_region_fail(self):
        response = {'regionRestriction': {'blocked': ['GB']}}
        self.assertFalse(Validate.region(response))

    def test_region_pass(self):
        response = {}
        self.assertTrue(Validate.region(response))

    def test_title_fail(self):
        response = {'title': 'Deutsch Trailer'}
        self.assertFalse(Validate.title(response))

    def test_title_pass(self):
        response = {'title': 'Trailer'}
        self.assertTrue(Validate.title(response))

    def test_channel_fail(self):
        response = {'channelTitle': '7even3hreetv'}
        self.assertFalse(Validate.channel_title(response))

    def test_channel_pass(self):
        response = {'channelTitle': 'paramount picture'}
        self.assertTrue(Validate.channel_title(response))

    def test_duration_pass(self):
        response = {'duration': 'PT04M15S'}
        self.assertTrue(Validate.duration(response))

    def test_duration_fail(self):
        response = {'duration': 'PT14M15S'}
        self.assertFalse(Validate.duration(response))

    def test_fix_duration(self):
        self.assertEqual(Validate.fix_duration('PT1H59M15S'), '119')
        self.assertEqual(Validate.fix_duration('PT04M15S'), '4')


class TestYouTubeVideo(unittest.TestCase):
    """Testing the class StandardiseResponse"""

    @classmethod
    def setUpClass(cls):
        cls.response = {
            'dislikeCount': '84',
            'duration': 'PT5M11S',
            'projection': 'rectangular',
            'definition': 'sd',
            'commentCount': '120',
            'etag': '"g7k5f8kvn67Bsl8L-Bum53neIr4/uXKmRwQj44qk2SrJnGXrybxn0ek"',
            'video_id': 'b1Stfe7Puk0',
            'favoriteCount': '0',
            'snippet': {
                'channelId': 'UC_G61kX-ORlltt4b20_Oriw',
                'publishedAt': '2016-03-29T09:42:39.000Z',
                'description': '',
                'localized': {
                    'description': '',
                    'title': 'Letta Mbulu - Nomalizo'
                },
                'title': 'Letta Mbulu - Nomalizo',
                'liveBroadcastContent': 'none',
                'tags': ['mr.chawaks'],
                'categoryId': '10',
                'channelTitle': 'Mr. Chawaks'
            },
            'viewCount': '448635',
            'id': 'b1Stfe7Puk0',
            'dimension': '2d',
            'kind': 'youtube#video',
            'caption': 'false',
            'likeCount': '6675',
            'licensedContent': False
        }

    def test_get_main_data(self):
        result = YouTubeVideo('tt1234567', self.response).main_data
        print(result)
        expected = {
            'channel_id': 'UC_G61kX-ORlltt4b20_Oriw',
            'duration': '5',
            'published_at': '2016-03-29',
            'view_count': 0,
            'definition': 'sd',
            'imdb_id': 'tt1234567',
            'video_id': 'b1Stfe7Puk0',
            'title': 'Letta Mbulu - Nomalizo',
            'channel_title': 'Mr. Chawaks'
        }
        #self.assertEqual(expected, result)

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






