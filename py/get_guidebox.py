import os

import guidebox

try:
    GUIDEBOX_API = os.environ['GUIDEBOX_API']
except KeyError:
    try:
        from GLOBALS import GUIDEBOX_API
    except ImportError:
        print("API is not known")
        exit()


class GetAPI(object):

    def __init__(self, api_key=GUIDEBOX_API):
        self.api_key = api_key
        guidebox.api_key = self.api_key
        self.source_topic = 'tmdb'
        self.destination_topic = 'guidebox'

    def get_info(self, request):
        imdb_id = request['imdb_id']
        result = {}
        movie = guidebox.Search.movies(field='id', id_type='imdb', query=imdb_id, region='gb')
        try:
            movie_info = guidebox.Movie.retrieve(movie['id'], region='gb')
        except KeyError:
            return result

        main_keys = ['duration', 'metacritic', 'title', 'overview', 'rating', 'release_date', 'id', 'wikipedia_id']
        result['guidebox_main'] = [dict({key: movie_info[key] for key in main_keys}, **{'imdb_id': imdb_id})]

        result['guidebox_cast'] = [{'name': x['name'],
                                    'imdb_id': imdb_id,
                                    'person_imdb_id': x['imdb']}

                                   for x in movie_info['cast']]

        result['guidebox_genres'] = [{'genre': x['title'],
                                      'imdb_id': imdb_id}
                                     for x in movie_info['genres']]

        result['guidebox_crew'] = []
        for role in ('directors', 'writers'):
            for person in movie_info[role]:
                result['guidebox_crew'].append({'imdb_id': imdb_id,
                                                'person_imdb_id': person['imdb'],
                                                'name': person['name'],
                                                'job': role[:-1]})

        result['guidebox_trailers'] = [dict(x, **{'imdb_id': imdb_id}) for x in movie_info['trailers']['web']]

        result['guidebox_sources'] = []
        result['guidebox_prices'] = []
        for source_type in ('free_web_sources', 'subscription_web_sources'):
            for source in movie_info[source_type]:
                result['guidebox_sources'].append(
                    dict(source, **{'imdb_id': imdb_id, 'type': source_type.split('_')[0]})
                )

        for source in movie_info['purchase_web_sources']:
            result['guidebox_sources'].append(
                dict({key: source[key] for key in ['display_name', 'link', 'source']},
                     **{'imdb_id': imdb_id, 'type': 'purchase'})
            )

            for format in source['formats']:
                result['guidebox_prices'].append(dict(format, **{'imdb_id': imdb_id, 'source': source['source']}))

            if source['source'] == 'google_play':
                youtube_source = {'imdb_id': imdb_id,
                                  'display_name': 'YouTube',
                                  'source': 'youtube',
                                  'link': 'https://www.youtube.com/watch?v=' + source['link'].split('=')[1],
                                  'type': 'purchase'}
                result['guidebox_sources'].append(youtube_source)
                for format in source['formats']:
                    result['guidebox_prices'].append(dict(format, **{'imdb_id': imdb_id, 'source': 'youtube'}))

        return result

