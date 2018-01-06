import sys
sys.path.append('..')

import unittest

from get_trailer import GetAPI, RequestAPI, StandardisedResponse, ChooseBest


class TestGetAPI(unittest.TestCase):
    """Testing RequestAPI"""
    @classmethod
    def setUpClass(cls):
        cls.get = GetAPI()

    def test_get_info(self):
        """
        Top level test checking that we pull back the bes trailer for a film
        """
        request = {'imdb_id': 'tt0117509',
                   'tmdb_main': [{'title': 'Blade Runner', 'release_date': '2000-01-01'}]}
        info = [e.main_data for e in self.get.get_info(request)]
        print(info)

class TestRequestAPI(unittest.TestCase):
    """Testing RequestAPI"""

    @classmethod
    def setUpClass(cls):
        cls.req = RequestAPI()

    def test_search_youtube(self):
        # Blade Runner
        title = 'Blade Runner hd trailer'
        response = self.req.get_trailer(title)
        print(response)

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
        responses = [{
            # Was published too long ago, should be dropped
            'definition': 'hd',
            'imdb_id': 'tt1234567',
            'duration': '2',
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
            'duration': '10',
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
            'duration': '3',
            'publishedAt': '2005-01-01',
            'channelId': 'abcde',
            'viewCount': '100',
            'video_id': '3',
            'channelTitle': 'TrailerChannel',
            'title': 'Awesome Movie - Trailer'
        }, {
            # SD trailer should be dropped
            'definition': 'sd',
            'imdb_id': 'tt1234567',
            'duration': '2',
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
            'duration': '3',
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
            'duration': '3',
            'publishedAt': '2005-01-01',
            'channelId': 'abcde',
            'viewCount': '50',
            'video_id': '6',
            'channelTitle': 'TrailerChannel',
            'title': 'Awesome Movie - Trailer'
        }]
        # Create response classes from our responses
        responses = [StandardisedResponse('tt1234567', e) for e in responses]
        a = ChooseBest().choose_best(responses, '2000-01-01', 'Awesome Movie')
        print(a)






