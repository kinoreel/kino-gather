import unittest
import os
import sys

current_dir = (os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(current_dir, '..', '..'))

from apis.get_trailer import GetAPI, YouTubeAPI, YouTubeVideo, ChooseBest, Validate


class TestGetAPI(unittest.TestCase):
    """Testing GetAPI"""

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

    def test_get_info_tmdb(self):
        """
        Top level test checking that we pull back the bes trailer for a film
        """
        request = {'imdb_id': 'tt0117509',
                   'tmdb_main': [{'title': 'Revolutionary Road', 'release_date': '2008-01-01'}],
                   'tmdb_trailer': [{'video_id': 'qADM67ZgYxM'}]}
        result = self.get.get_info(request)
        expected = {
            'trailer_main': [{
                'channel_id': 'UC9YHyj7QSkkSg2pjQ7M8Khg',
                'view_count': '1383642',
                'definition': 'hd',
                'imdb_id': 'tt0117509',
                'duration': '2',
                'dislike_count': '0',
                'published_at': '2012-10-15',
                'comment_count': '0',
                'title': 'Revolutionary Road - Trailer',
                'channel_title': 'Paramount Movies',
                'video_id': 'qADM67ZgYxM',
                'like_count': '0'
            }]
        }
        self.assertEqual(result, expected)

    def test_get_info_no_tmdb_trailer(self):
        """
        Top level test checking that we pull back the bes trailer for a film
        """
        request = {'imdb_id': 'tt0117509',
                   'tmdb_main': [{'title': 'Revolutionary Road', 'release_date': '2008-01-01'}],
                   'tmdb_trailer': []}
        result = self.get.get_info(request)
        expected = {
            'trailer_main': [{
                'video_id': 'qADM67ZgYxM',
                'imdb_id': 'tt0117509',
                'comment_count': '0',
                'title': 'Revolutionary Road - Trailer',
                'duration': '2',
                'view_count': '1383642',
                'definition': 'hd',
                'channel_title': 'Paramount Movies',
                'published_at': '2012-10-15',
                'channel_id': 'UC9YHyj7QSkkSg2pjQ7M8Khg',
                'dislike_count': '0',
                'like_count': '0'
            }]
        }
        self.assertEqual(result, expected)

    def test_get_info_invalid_tmdb_trailer(self):
        """
        Top level test checking that we pull back the bes trailer for a film
        """
        request = {'imdb_id': 'tt0117509',
                   'tmdb_main': [{'title': 'Revolutionary Road', 'release_date': '2008-01-01'}],
                   'tmdb_trailer': [{'video_id': 'invalid'}]}
        result = self.get.get_info(request)
        expected = {
            'trailer_main': [{
                'video_id': 'qADM67ZgYxM',
                'published_at': '2012-10-15',
                'title': 'Revolutionary Road - Trailer',
                'channel_title': 'Paramount Movies',
                'imdb_id': 'tt0117509',
                'like_count': '0',
                'view_count': '1383642',
                'comment_count': '0',
                'definition': 'hd',
                'dislike_count': '0',
                'channel_id': 'UC9YHyj7QSkkSg2pjQ7M8Khg',
                'duration': '2'
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
            'viewCount': '2196',
            'caption': 'false',
            'favoriteCount': '0',
            'duration': 'PT2M12S',
            'commentCount': '2',
            'kind': 'youtube#searchResult',
            'etag': '"g7k5f8kvn67Bsl8L-Bum53neIr4/8PKD9P0S8VNnrAApwjApZal_kqQ"',
            'likeCount': '3',
            'licensedContent': False,
            'snippet': {
                'channelId': 'UCKZ6PGIA7btRoZWRcqj4Yxw',
                'channelTitle': 'The Movie Planet',
                'title': 'Revolutionary Road (2008) trailer',
                'liveBroadcastContent': 'none',
                'publishedAt': '2008-09-30T09:42:40.000Z',
                'description': 'More here: http://themovieplanet.wordpress.com/2008/10/03/new-trailer-and-poster-'
                               'revolutionary-road/ Directed by Sam Mendes Written by Justin Haythe, based '
                               'on a novel by Richard Yates ...'
            },
            'definition': 'sd',
            'dislikeCount': '1',
            'projection': 'rectangular',
            'video_id': 'Dz7HszUJs0A',
            'dimension': '2d'
        }

    def test_get_main_data(self):
        result = YouTubeVideo('tt1234567', self.response).main_data
        expected = {
            'published_at': '2008-09-30',
            'imdb_id': 'tt1234567',
            'channel_id': 'UCKZ6PGIA7btRoZWRcqj4Yxw',
            'view_count': '2196',
            'duration': '2',
            'channel_title': 'The Movie Planet',
            'video_id': 'Dz7HszUJs0A',
            'title': 'Revolutionary Road (2008) trailer',
            'definition': 'sd',
            'comment_count': '0',
            'dislike_count': '1',
            'like_count': '3'
        }
        self.assertEqual(expected, result)


class TestChooseBest(unittest.TestCase):
    """Testing the ChooseBest class"""


    @classmethod
    def setUpClass(cls):
        imdb_id = 'tt0959337'
        response = [{
            'viewCount': '2196',
            'caption': 'false',
            'favoriteCount': '0',
            'duration': 'PT2M12S',
            'commentCount': '2',
            'kind': 'youtube#searchResult',
            'etag': '"g7k5f8kvn67Bsl8L-Bum53neIr4/8PKD9P0S8VNnrAApwjApZal_kqQ"',
            'likeCount': '3',
            'licensedContent': False,
            'snippet': {
                'channelId': 'UCKZ6PGIA7btRoZWRcqj4Yxw',
                'channelTitle': 'The Movie Planet',
                'title': 'Revolutionary Road (2008) trailer',
                'liveBroadcastContent': 'none',
                'publishedAt': '2008-09-30T09:42:40.000Z',
                'description': 'More here: http://themovieplanet.wordpress.com/2008/10/03/new-trailer-and-poster-revolutionary-road/ Directed by Sam Mendes Written by Justin Haythe, based on a novel by Richard Yates ...'
            },
            'definition': 'sd',
            'dislikeCount': '1',
            'projection': 'rectangular',
            'video_id': 'Dz7HszUJs0A',
            'dimension': '2d'
        }, {
            'viewCount': '1378734',
            'caption': 'false',
            'favoriteCount': '0',
            'duration': 'PT2M10S',
            'kind': 'youtube#searchResult',
            'etag': '"g7k5f8kvn67Bsl8L-Bum53neIr4/0BvpscI2iO9QEbHkmZcn3jO7KKk"',
            'licensedContent': True,
            'snippet': {
                'channelId': 'UC9YHyj7QSkkSg2pjQ7M8Khg',
                'channelTitle': 'Paramount Movies',
                'title': 'Revolutionary Road - Trailer',
                'liveBroadcastContent': 'none',
                'publishedAt': '2012-10-15T16:50:49.000Z',
                'description': 'Academy Award® nominee Leonardo DiCaprio* and Academy Award® winner Kate Winslet** reunite for two powerful, groundbreaking performances in Revolutionary Road. Based on the bestseller by...'
            },
            'definition': 'hd',
            'projection': 'rectangular',
            'video_id': 'qADM67ZgYxM',
            'dimension': '2d'
        }]
        cls.videos = [YouTubeVideo(imdb_id, e) for e in response]

    def test_sort_by_view_count(self):
        result = ChooseBest().sort_by_view_count(self.videos)
        view_counts = [e.main_data['view_count'] for e in result]
        self.assertTrue(all(int(view_counts[i]) > int(view_counts[i+1]) for i in range(0, len(view_counts) - 1)))

    def test_get_hd(self):
        result = ChooseBest().get_hd_videos(self.videos)
        result = [e.main_data['video_id'] for e in result]
        expected = ['qADM67ZgYxM']
        self.assertEqual(result, expected)

    def test_choose_best(self):
        result = ChooseBest().choose_best(self.videos)
        result = result.main_data['video_id']
        expected = 'qADM67ZgYxM'
        self.assertEqual(result, expected)



