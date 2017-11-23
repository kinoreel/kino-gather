import sys
sys.path.append('..')

import unittest

from get_tmdb import GetAPI, RequestAPI, StandardiseResponse
from GatherException import GatherException

class TestGetAPI(unittest.TestCase):
    """Testing GetAPI"""
    @classmethod
    def setUpClass(cls):
        cls.get = GetAPI()

    def test_get_info(self):
        # Check get_info for a correct imdb_id
        request = {'imdb_id': 'tt0083658'}
        expected_keys= ['tmdb_main', 'tmdb_cast', 'tmdb_crew', 'tmdb_company', 'tmdb_genre', 'tmdb_keywords',
                        'tmdb_trailer']
        info = self.get.get_info(request)
        self.assertEqual(set(info.keys()), set(expected_keys))


class TestRequestAPI(unittest.TestCase):
    """Testing RequestAPI"""

    @classmethod
    def setUpClass(cls):
        cls.req = RequestAPI()

    def test_get_tmdb(self):
        # Blade Runner
        imdb_id = 'tt0083658'
        response = self.req.get_tmdb(imdb_id)
        self.assertEqual(response['title'], 'Blade Runner')
        self.assertEqual(response['imdb_id'], imdb_id)

        # Run Lola Run
        imdb_id = 'tt0130827'
        response = self.req.get_tmdb(imdb_id)
        self.assertEqual(response['title'], 'Run Lola Run')
        self.assertEqual(response['imdb_id'], imdb_id)

        # True Grit - 1969
        # Testing that the release year is not appending for films
        # that have been remade.
        imdb_id = 'tt0065126'
        response = self.req.get_tmdb(imdb_id)
        self.assertEqual(response['title'], 'True Grit')
        self.assertEqual(response['imdb_id'], imdb_id)

        # Bad imdb_id
        imdb_id = 'tt1234578'
        self.assertRaises(GatherException, self.req.get_tmdb, imdb_id)

class TestStandardiseResponse(unittest.TestCase):
    """Testing StardardiseResponse"""

    @classmethod
    def setUpClass(cls):
        cls.stan = StandardiseResponse()
        cls.imdb_id = 'tt0083658'
        # Shortened response for Blade Runner from the TMDB API.
        cls.response = {
            'budget': 28000000,
            'overview': 'In the smog-choked dystopian Los Angeles of 2019, blade runner Rick Deckard is called out of retirement to terminate a quartet of replicants who have escaped to Earth seeking their creator for a way to extend their short life spans.',
            'tagline': "Man has made his match... now it's his problem.",
            'release_date': '1982-06-25',
            'id': 78,
            'status': 'Released',
            'title': 'Blade Runner',
            'popularity': 102.026128,
            'credits': {
                'crew': [{
                    'name': 'Ridley Scott',
                    'credit_id': '52fe4214c3a36847f8002595',
                    'gender': 2,
                    'profile_path': '/oTAL0z0vsjipCruxXUsDUIieuhk.jpg',
                    'id': 578,
                    'job': 'Director',
                    'department': 'Directing'
                }, {
                    'name': 'Michael Deeley',
                    'credit_id': '52fe4214c3a36847f800259b',
                    'gender': 2,
                    'profile_path': None,
                    'id': 581,
                    'job': 'Producer',
                    'department': 'Production'
                }, {
                    'name': 'Jordan Cronenweth',
                    'credit_id': '52fe4214c3a36847f80025c9',
                    'gender': 2,
                    'profile_path': None,
                    'id': 594,
                    'job': 'Director of Photography',
                    'department': 'Camera'
                }],
                'cast': [{
                    'cast_id': 6,
                    'character': 'Rick Deckard',
                    'credit_id': '52fe4214c3a36847f800259f',
                    'order': 0,
                    'gender': 2,
                    'id': 3,
                    'name': 'Harrison Ford',
                    'profile_path': '/7CcoVFTogQgex2kJkXKMe8qHZrC.jpg'
                }, {
                    'cast_id': 7,
                    'character': 'Roy Batty',
                    'credit_id': '52fe4214c3a36847f80025a3',
                    'order': 1,
                    'gender': 2,
                    'id': 585,
                    'name': 'Rutger Hauer',
                    'profile_path': '/2x1S2VAUvZXZuDjZ4E9iEKINvNu.jpg'
                }, {
                    'cast_id': 8,
                    'character': 'Rachael',
                    'credit_id': '52fe4214c3a36847f80025a7',
                    'order': 2,
                    'gender': 1,
                    'id': 586,
                    'name': 'Sean Young',
                    'profile_path': '/4zgkRFQruIlaJ4JakNZLoKJ70fH.jpg'
                }]
            },
            'backdrop_path': '/5hJ0XDCxE3qGfp1H3h7HQP9rLfU.jpg',
            'original_title': 'Blade Runner',
            'belongs_to_collection': {
                'poster_path': '/foT46aJ7QPUFDl3CK8ArDl0JaZX.jpg',
                'backdrop_path': '/57zhlMYblPute6qb8v16ZmGSPVv.jpg',
                'id': 422837,
                'name': 'Blade Runner Collection'
            },
            'vote_average': 7.9,
            'production_companies': [{
                'id': 5798,
                'name': 'Shaw Brothers'
            }, {
                'id': 6194,
                'name': 'Warner Bros.'
            }, {
                'id': 7965,
                'name': 'The Ladd Company'
            }],
            'adult': False,
            'original_language': 'en',
            'spoken_languages': [{
                'iso_639_1': 'en',
                'name': 'English'
            }, {
                'iso_639_1': 'de',
                'name': 'Deutsch'
            }, {
                'iso_639_1': 'cn',
                'name': '广州话 / 廣州話'
            }, {
                'iso_639_1': 'ja',
                'name': '日本語'
            }, {
                'iso_639_1': 'hu',
                'name': 'Magyar'
            }],
            'imdb_id': 'tt0083658',
            'genres': [{
                'id': 878,
                'name': 'Science Fiction'
            }, {
                'id': 18,
                'name': 'Drama'
            }, {
                'id': 53,
                'name': 'Thriller'
            }],
            'production_countries': [{
                'iso_3166_1': 'US',
                'name': 'United States of America'
            }, {
                'iso_3166_1': 'HK',
                'name': 'Hong Kong'
            }, {
                'iso_3166_1': 'GB',
                'name': 'United Kingdom'
            }],
            'keywords': {
                'keywords': [{
                    'id': 310,
                    'name': 'artificial intelligence'
                }, {
                    'id': 801,
                    'name': 'bounty hunter'
                }]
            },
            'video': False,
            'poster_path': '/p64TtbZGCElxQHpAMWmDHkWJlH2.jpg',
            'homepage': 'http://www.warnerbros.com/blade-runner',
            'videos': {
                'results': [{
                    'key': 'PSIiGE105iA',
                    'type': 'Featurette',
                    'name': 'Harrison Ford On Blade Runner',
                    'iso_639_1': 'en',
                    'id': '533ec651c3a368544800008a',
                    'site': 'YouTube',
                    'iso_3166_1': 'US',
                    'size': 480
                }, {
                    'key': 'W_9rhPDLHWk',
                    'type': 'Trailer',
                    'name': 'The Final Cut trailer',
                    'iso_639_1': 'en',
                    'id': '54ff5ca09251413d9b00032c',
                    'site': 'YouTube',
                    'iso_3166_1': 'US',
                    'size': 1080
                }, {
                    'key': 'AQL9hRRYDIw',
                    'type': 'Trailer',
                    'name': 'Trailer',
                    'iso_639_1': 'en',
                    'id': '586522349251412b8701d59c',
                    'site': 'YouTube',
                    'iso_3166_1': 'US',
                    'size': 480
                }]
            },
            'vote_count': 3912,
            'revenue': 33139618,
            'runtime': 117
        }

    def test_get_main_data(self):
        expected_result = [{'title': 'Blade Runner', 'runtime': 117, 'revenue': 33139618, 'budget': 28000000,
                            'imdb_id': 'tt0083658', 'original_language': 'en','release_date': '1982-06-25',
                            'plot': 'In the smog-choked dystopian Los Angeles of 2019, blade runner Rick Deckard is called out of retirement to terminate a quartet of replicants who have escaped to Earth seeking their creator for a way to extend their short life spans.'
                           }]
        main_data = self.stan.get_main_data(self.imdb_id, self.response)
        self.assertEqual(expected_result, main_data)

    def test_get_crew_data(self):
        expected_result = [{'name': 'Ridley Scott', 'imdb_id': 'tt0083658', 'role': 'director'},
                           {'name': 'Michael Deeley', 'imdb_id': 'tt0083658', 'role': 'producer'},
                           {'name': 'Jordan Cronenweth', 'imdb_id': 'tt0083658', 'role': 'director of photography'}]
        crew_data = self.stan.get_crew_data(self.imdb_id, self.response)
        self.assertEqual(crew_data, expected_result)

    def test_get_cast_data(self):
        expected_result = [{'imdb_id': 'tt0083658', 'name': 'Harrison Ford', 'role': 'actor', 'cast_order': 0},
                           {'imdb_id': 'tt0083658', 'name': 'Rutger Hauer', 'role': 'actor', 'cast_order': 1},
                           {'imdb_id': 'tt0083658', 'name': 'Sean Young', 'role': 'actor', 'cast_order': 2}]
        cast_data = self.stan.get_cast_data(self.imdb_id, self.response)
        self.assertEqual(cast_data, expected_result)

    def test_get_keyword_data(self):
        expected_result = [{'keyword': 'artificial intelligence', 'imdb_id': 'tt0083658'},
                           {'keyword': 'bounty hunter', 'imdb_id': 'tt0083658'}]
        keywords_data = self.stan.get_keywords_data(self.imdb_id, self.response)
        self.assertEqual(keywords_data, expected_result)

    def test_get_genre_data(self):
        expected_result = [{'genre': 'Science Fiction', 'imdb_id': 'tt0083658'},
                           {'genre': 'Drama', 'imdb_id': 'tt0083658'},
                           {'genre': 'Thriller', 'imdb_id': 'tt0083658'}]
        genre_data = self.stan.get_genre_data(self.imdb_id, self.response)
        self.assertEqual(genre_data, expected_result)

    def test_get_company_data(self):
        expected_result = [{'name': 'Shaw Brothers', 'imdb_id': 'tt0083658'},
                           {'name': 'Warner Bros.', 'imdb_id': 'tt0083658'},
                           {'name': 'The Ladd Company', 'imdb_id': 'tt0083658'}]
        company_data = self.stan.get_company_data(self.imdb_id, self.response)
        self.assertEqual(company_data, expected_result)

    def test_get_trailer_data(self):
        expected_result = [{'url': 'W_9rhPDLHWk', 'imdb_id': 'tt0083658'}]
        trailer_data = self.stan.get_trailer_data(self.imdb_id, self.response)
        self.assertEqual(trailer_data, expected_result)

    def test_sort_video_list_trailer(self):
        video_list = [{
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
        video_list = self.stan.sort_videos_list(video_list)
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
        video_list = self.stan.sort_videos_list(video_list)
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
        video_list = self.stan.sort_videos_list(video_list)
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

    def test_sort_video_list_(self):
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
        video_list = self.stan.sort_videos_list(video_list)
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


