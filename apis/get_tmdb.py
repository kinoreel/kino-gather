import json
import os
import requests

from apis.GatherException import GatherException

try:
    TMDB_API = os.environ['API_KEY']
except KeyError:
    try:
        from apis.GLOBALS import TMDB_API
    except ImportError:
        print("API is not known")
        exit()


class GetAPI(object):
    """
    Top level class imported by kafka_apis.py.
    Gets and standardises data from TMDB api for a given imdb_id.
    The class also hold responsibility of the topic it consumes from and the topic it produces to.
    """

    def __init__(self):
        self.source_topic = 'omdb'
        self.destination_topic = 'tmdb'

    def get_info(self, request):
        imdb_id = request['imdb_id']
        data = RequestAPI().get_tmdb(imdb_id)
        data = StandardiseResponse().standardise(imdb_id, data)
        return data


class RequestAPI(object):
    """This class requests data for a given imdb_id from the TMDB API."""

    def __init__(self, api_key=TMDB_API):
        self.api_key = api_key
        self.headers = {'User-Agent':
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    def get_tmdb(self, imdb_id):
        """
        For a given imdb_id, we construct the API url, make a get request,
        and return the response as a JSON object.
        :param imdb_id: The imdb_id of the film we are requesting.
        :return: A JSON object containing the response for the given imdb_id.
        """
        request_url = 'https://api.themoviedb.org/3/movie/{0}?api_key={1}&append_to_response={2}'
        requested_data = 'credits,videos,keywords'
        request_url = request_url.format(imdb_id, self.api_key, requested_data)
        html = requests.get(request_url)
        data = json.loads(html.text)
        if data.get('imdb_id') == imdb_id:
            return data
        else:
            raise GatherException(imdb_id, 'No response from TMDB API')


class StandardiseResponse(object):
    """
    This class reconstructs the response returned from the TMDB API, making
    a new JSON object that is easier to handle for later applications.
    """

    def standardise(self, imdb_id, api_data):
        """
        We construct a new dictionary from teh API data, standardising the format
        so we it can be handled easily in later applications.
        :param imdb_id: The imdb_id for the film that was requested from OMDB API
        :param api_data: The raw response from teh OMDB API
        :return: A standardised dictionary.
        """
        main_data = self.get_main_data(imdb_id, api_data)
        cast_data = self.get_cast_data(imdb_id, api_data)
        crew_data = self.get_crew_data(imdb_id, api_data)
        keywords_data = self.get_keywords_data(imdb_id, api_data)
        genre_data = self.get_genre_data(imdb_id, api_data)
        company_data = self.get_company_data(imdb_id, api_data)
        trailer_data = self.get_trailer_data(imdb_id, api_data)

        return {'tmdb_main': main_data,
                'tmdb_crew': crew_data,
                'tmdb_cast': cast_data,
                'tmdb_keywords': keywords_data,
                'tmdb_genre': genre_data,
                'tmdb_company': company_data,
                'tmdb_trailer': trailer_data}

    @staticmethod
    def get_main_data(imdb_id, api_data):
        """
        Gets the main data returned by the TMDB API, and constructs a dictonary
        of this information.
        :param imdb_id: The imdb_id for the film we requested
        :param api_data: The OMDB API response
        :return: A single entry array containing the main info for the film.
        """
        try:
            main_data = [{'imdb_id': imdb_id,
                          'title': api_data['title'],
                          'release_date': api_data['release_date'],
                          'plot': api_data['overview'],
                          'original_language': api_data['original_language'],
                          'runtime': api_data['runtime'],
                          'revenue': api_data['revenue'],
                          'budget': api_data['budget']}]
        except:
            raise GatherException(imdb_id, 'No main data could be found from TMDB')

        return main_data

    @staticmethod
    def get_cast_data(imdb_id, api_data):
        """
        Gets the cast data returned by the TMDB API.
        :param imdb_id: The imdb_id for the requested film.
        :param api_data: The TMDB API response
        :return: A array of dictionaries - imdb_id, name, role - for the cast in the film
        """
        cast_data = [{'imdb_id': imdb_id,
                      'name': e['name'],
                      'role': 'actor',
                      'cast_order': e['order']} for e in api_data["credits"]["cast"]]

        return cast_data

    @staticmethod
    def get_crew_data(imdb_id, api_data):
        """
        Gets the crew data returned by the TMDB API.
        :param imdb_id: The imdb_id for the requested film.
        :param api_data: The TMDB API response
        :return: A array of dictionaries - imdb_id, name, role - for the cast in the film
        """
        crew_data = [{'imdb_id': imdb_id,
                      'name': e['name'],
                      'role': e['job'].lower()} for e in api_data["credits"]["crew"]]

        return crew_data

    @staticmethod
    def get_keywords_data(imdb_id, api_data):
        """
        Gets the keyword data returned by the TMDB API.
        :param imdb_id: The imdb_id for the requested film.
        :param api_data: The TMDB API response
        :return: A array of dictionaries - imdb_id, keyword.
        """
        keywords_data = []
        for keyword in api_data["keywords"]["keywords"]:
            keywords_data.append({'imdb_id': imdb_id, 'keyword': keyword['name']})
        return keywords_data

    @staticmethod
    def get_genre_data(imdb_id, api_data):
        """
        Gets the genre data returned by the TMDB API.
        :param imdb_id: The imdb_id for the requested film.
        :param api_data: The TMDB API response
        :return: A array of dictionaries - imdb_id, genre.
        """
        genre_data = [{'imdb_id': imdb_id,
                       'genre': e['name']} for e in api_data["genres"]]

        return genre_data

    @staticmethod
    def get_company_data(imdb_id, api_data):
        """
        Gets the company data returned by the TMDB API.
        :param imdb_id: The imdb_id for the requested film.
        :param api_data: The TMDB API response
        :return: A array of dictionaries - imdb_id, company, role.
        """
        company_data = []
        for company in api_data["production_companies"]:
            company_data.append({'imdb_id': imdb_id, 'name': company['name']})
        return company_data

    @staticmethod
    def get_trailer_data(imdb_id, api_data):
        """
        Gets the trailer data returned by the TMDB API. We choose the best video based on
        an ordering/criteria determined by the function order_video_list.
        :param imdb_id: The imdb_id for the requested film.
        :param api_data: The TMDB API response
        :return: A array of dictionaries - imdb_id, url.
        """
        # We get all videos that are specified as trailers that are hosted on youtube and are in English.
        videos = [e for e in api_data["videos"]["results"]
                  if e['type'].lower() == 'trailer' and
                  e['site'].lower() == 'youtube' and
                  e['iso_639_1'].lower() == 'en']

        try:
            best_trailer = StandardiseResponse.sort_videos_list(videos)[0]
        except IndexError:
            return []

        trailer_data = [{'imdb_id': imdb_id,
                         'video_id': best_trailer['key'],
                         'size': best_trailer['size']},
                        ]

        return trailer_data

    @staticmethod
    def sort_videos_list(video_list):
        """
        Orders the list of videos based on the following criteria:
        - The video title contains the word 'trailer'
        - The video title contains the word 'official'
        - The quality/size of the video.
        :param video_list: A list of videos
        :return: An list of videos ordered by chosen criteria
        """
        video_list = sorted(video_list, key=lambda x: x['size'], reverse=True)
        video_list = sorted(video_list, key=lambda x: 'official' in x['name'].lower(), reverse=True)
        video_list = sorted(video_list, key=lambda x: 'trailer' in x['name'].lower(), reverse=True)
        return video_list
