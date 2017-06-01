import guidebox


class GetGuidebox:

    def __init__(self, api_key):
        guidebox.api_key = api_key

    def get_info(self, imdb_id):
        result = {}
        movie = guidebox.Search.movies(field='id', id_type='imdb', query=imdb_id, region='gb')
        try:
            movie_info = guidebox.Movie.retrieve(movie['id'], region='gb')
        except KeyError:
            return result

        main_keys = ['duration', 'metacritic', 'title', 'overview', 'rating', 'release_date', 'id', 'wikipedia_id']
        result['guidebox_main'] = [dict({key: movie_info[key] for key in main_keys}, **{'imdb_id': imdb_id})]

        result['guidebox_cast'] = [{'name': x['name'],
                                    'movie_imdb_id': imdb_id,
                                    'imdb_id': x['imdb']}
                                   for x in movie_info['cast']]

        result['guidebox_genres'] = [{'genre': x['title'],
                                      'imdb_id': imdb_id}
                                     for x in movie_info['genres']]

        result['guidebox_crew'] = []
        for role in ('directors', 'writers'):
            for person in movie_info[role]:
                result['guidebox_crew'].append({'movie_imdb_id': imdb_id,
                                                'imdb_id': person['imdb'],
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

    # DB TABLES
    # guidebox_cast: imdb_id, movie_imdb_id, name
    # guidebox_main: imdb_id, id, rating, duration, overview, title, release_date, wikipedia_id, metacritic
    # guidebox_genres: imdb_id, genre
    # guidebox_prices: imdb_id, price, pre_order, format, type, source
    # guidebox_trailers: imdb_id, source, embed, display_name, link, type
    # guidebox_crew: imdb_id, job, name, movie_imdb_id
    # guidebox_sources: imdb_id, source, link, display_name, type
