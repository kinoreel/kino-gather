import json
import unittest

from apis import GLOBALS
from apis.get_tmdb import GetAPI

class TestGetTMDB(unittest.TestCase):

    def test_sort_video_list_trailer(self):

        get = GetAPI()
        video_list =  [{
            'id': '000000',
            'key': 'abcde',
            'imdb_id': 'tt0000000',
            'type': 'Trailer',
            'site': 'YouTube',
            'iso_3166_1': 'US',
            'name': 'Tv Promo',
            'iso_639_1': 'en',
            'size': 1080
        }, {
            'id': '000000',
            'key': 'abcde',
            'imdb_id': 'tt0000000',
            'type': 'Trailer',
            'site': 'YouTube',
            'iso_3166_1': 'US',
            'name': 'Trailer',
            'iso_639_1': 'en',
            'size': 1080
        }]
        video_list = get.sort_videos_list(video_list)
        self.assertEqual(video_list, [{ 'id': '000000',
                                        'key': 'abcde',
                                        'imdb_id': 'tt0000000',
                                        'type': 'Trailer',
                                        'site': 'YouTube',
                                        'iso_3166_1': 'US',
                                        'name': 'Trailer',
                                        'iso_639_1': 'en',
                                        'size': 1080
                                    }, {
                                        'id': '000000',
                                        'key': 'abcde',
                                        'imdb_id': 'tt0000000',
                                        'type': 'Trailer',
                                        'site': 'YouTube',
                                        'iso_3166_1': 'US',
                                        'name': 'Tv Promo',
                                        'iso_639_1': 'en',
                                        'size': 1080
                                    }])

    def test_sort_video_list_official(self):
        get = GetAPI()
        video_list = [{
            'id': '000000',
            'key': 'abcde',
            'imdb_id': 'tt0000000',
            'type': 'Trailer',
            'site': 'YouTube',
            'iso_3166_1': 'US',
            'name': 'Official video',
            'iso_639_1': 'en',
            'size': 1080
        }, {
            'id': '000000',
            'key': 'abcde',
            'imdb_id': 'tt0000000',
            'type': 'Trailer',
            'site': 'YouTube',
            'iso_3166_1': 'US',
            'name': 'Video',
            'iso_639_1': 'en',
            'size': 1080
        }]
        video_list = get.sort_videos_list(video_list)
        self.assertEqual(video_list, [{'id': '000000',
                                       'key': 'abcde',
                                       'imdb_id': 'tt0000000',
                                       'type': 'Trailer',
                                       'site': 'YouTube',
                                       'iso_3166_1': 'US',
                                       'name': 'Official video',
                                       'iso_639_1': 'en',
                                       'size': 1080
                                    }, {
                                       'id': '000000',
                                       'key': 'abcde',
                                       'imdb_id': 'tt0000000',
                                       'type': 'Trailer',
                                       'site': 'YouTube',
                                       'iso_3166_1': 'US',
                                       'name': 'Video',
                                       'iso_639_1': 'en',
                                       'size': 1080
                                      }])


    def test_sort_video_list_size(self):
        get = GetAPI()
        video_list = [{
            'id': '000000',
            'key': 'abcde',
            'imdb_id': 'tt0000000',
            'type': 'Trailer',
            'site': 'YouTube',
            'iso_3166_1': 'US',
            'name': 'Official Trailer',
            'iso_639_1': 'en',
            'size': 720
        }, {
            'id': '000000',
            'key': 'abcde',
            'imdb_id': 'tt0000000',
            'type': 'Trailer',
            'site': 'YouTube',
            'iso_3166_1': 'US',
            'name': 'Official Trailer',
            'iso_639_1': 'en',
            'size': 1080
        }]
        video_list = get.sort_videos_list(video_list)
        self.assertEqual(video_list, [{'id': '000000',
                                       'key': 'abcde',
                                       'imdb_id': 'tt0000000',
                                       'type': 'Trailer',
                                       'site': 'YouTube',
                                       'iso_3166_1': 'US',
                                       'name': 'Official Trailer',
                                       'iso_639_1': 'en',
                                       'size': 1080
                                    }, {'id': '000000',
                                        'key': 'abcde',
                                        'imdb_id': 'tt0000000',
                                        'type': 'Trailer',
                                        'site': 'YouTube',
                                        'iso_3166_1': 'US',
                                        'name': 'Official Trailer',
                                        'iso_639_1': 'en',
                                        'size': 720
                                    }])

    def test_sort_video_list_size(self):
        get = GetAPI()
        video_list = [ {
            'id': '000000',
            'key': 'abcde',
            'imdb_id': 'tt0000000',
            'type': 'Trailer',
            'site': 'YouTube',
            'iso_3166_1': 'US',
            'name': 'Official Video',
            'iso_639_1': 'en',
            'size': 720
        }, {
            'id': '000000',
            'key': 'abcde',
            'imdb_id': 'tt0000000',
            'type': 'Trailer',
            'site': 'YouTube',
            'iso_3166_1': 'US',
            'name': 'Trailer',
            'iso_639_1': 'en',
            'size': 480
        }, {
            'id': '000000',
            'key': 'abcde',
            'imdb_id': 'tt0000000',
            'type': 'Trailer',
            'site': 'YouTube',
            'iso_3166_1': 'US',
            'name': 'Random Video',
            'iso_639_1': 'en',
            'size': 1080
        }]
        video_list = get.sort_videos_list(video_list)
        self.assertEqual(video_list, [{ 'id': '000000',
                                        'key': 'abcde',
                                        'imdb_id': 'tt0000000',
                                        'type': 'Trailer',
                                        'site': 'YouTube',
                                        'iso_3166_1': 'US',
                                        'name': 'Trailer',
                                        'iso_639_1': 'en',
                                        'size': 480
                                    }, {
                                        'id': '000000',
                                        'key': 'abcde',
                                        'imdb_id': 'tt0000000',
                                        'type': 'Trailer',
                                        'site': 'YouTube',
                                        'iso_3166_1': 'US',
                                        'name': 'Official Video',
                                        'iso_639_1': 'en',
                                        'size': 720
                                    }, {
                                        'id': '000000',
                                        'key': 'abcde',
                                        'imdb_id': 'tt0000000',
                                        'type': 'Trailer',
                                        'site': 'YouTube',
                                        'iso_3166_1': 'US',
                                        'name': 'Random Video',
                                        'iso_639_1': 'en',
                                        'size': 1080
                                    }])

if __name__=='__main__':
    unittest.main()


