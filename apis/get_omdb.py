import json
import os
import requests
import re

from apis.GatherException import GatherException

try:
    OMDB_API = os.environ['API_KEY']
except KeyError:
    try:
        from apis.GLOBALS import OMDB_API
    except ImportError:
        print("API is not known")
        exit()


class GetAPI(object):
    """
    Top level class imported by kafka_apis.py.
    Gets and standardises data from OMDB api for a given imdb_id.
    The class also hold responsibility of the topic it consumes from and the topic it produces to.
    """

    def __init__(self):
        self.source_topic = 'imdb_ids'
        self.destination_topic = 'omdb'

    def get_info(self, request):
        imdb_id = request['imdb_id']
        data = RequestAPI().get_omdb(imdb_id)
        data = StandardiseResponse().standardise(imdb_id, data)
        return data


class RequestAPI(object):
    """Requests data for a given imdb_id from the OMDB API."""

    def __init__(self, api_key=OMDB_API):
        self.api_key = api_key
        self.headers = {'User-Agent':
                        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    def get_omdb(self, imdb_id):
        """
        For a given imdb_id, we construct the API url, make a get request,
        and return the response as a JSON object.
        :param imdb_id: The imdb_id of the film we are requesting.
        :return: A JSON object containing the response for the given imdb_id.
        """
        request_url = 'http://www.omdbapi.com/?i={0}&apikey={1}'.format(imdb_id, self.api_key)
        html = requests.get(request_url, headers=self.headers)
        data = json.loads(html.text)
        if data['Response'] == 'True':
            return data
        else:
            raise GatherException(imdb_id, 'No response from OMDB API')


class StandardiseResponse(object):
    """
    This class standardises the response returned from the OMDB API,
    removing unwanted data, and structuring the remaining data
    so that it is easier to handle in later processes.
    """

    def standardise(self, imdb_id, api_data):
        """
        Constructs a new dictionary from the API data.
        :param imdb_id: The imdb_id for the requested film
        :param api_data: The raw response from the OMDB API
        :return: A standardised dictionary.
        """
        main_data = self.get_main_data(imdb_id, api_data)
        ratings_data = self.get_ratings_data(imdb_id, api_data)
        if ratings_data and main_data:
            return {'omdb_main': main_data, 'omdb_ratings': ratings_data}
        else:
            raise GatherException(imdb_id, 'Failed standardise')

    @staticmethod
    def get_main_data(imdb_id, api_data):
        """
        Gets the main data returned by the OMDB API, and constructs a dictionary
        of this information.
        :param imdb_id: The imdb_id for the requested film
        :param api_data: The raw response from the OMDB API.
        :return: A dictionary containing the main data from the OMDB api
        """
        try:
            main_data = [{'imdb_id': imdb_id,
                          'title': api_data['Title'],
                          'language': api_data['Language'],
                          'rated': api_data['Rated'].replace('N/A', '').replace('NOT RATED', '').replace('UNRATED', ''),
                          'plot': api_data['Plot'],
                          'country': api_data['Country']
                          }]
        except KeyError:
            raise GatherException('No main data could be found from OMDB')
        return main_data

    @staticmethod
    def get_ratings_data(imdb_id, api_data):
        """
        Gets the rating data returned by the OMDB API, and creates a list of dictionaries
        of ratings information.
        :param imdb_id: The imdb_id for the requested film
        :param api_data: The raw response from the OMDB API.
        :return: A array of dictionaries - imdb_id, source, value - for the film ratings
        """
        ratings_data = []

        if 'Metascore' in api_data.keys():
            try:
                value = int(api_data['Metascore'])
                ratings_data.append({'imdb_id': imdb_id, 'source': 'metascore', 'value': value})
            # Metascore is sometimes returned as 'N/A'
            except ValueError:
                pass

        if 'imdbRating' in api_data.keys():
            ratings_data.append({'imdb_id': imdb_id, 'source': 'imdb', 'value': api_data['imdbRating']})

        if 'Ratings' in api_data.keys():
            for rating in api_data['Ratings']:
                # Each rating is already a dictionary containing two key values - Source and Value.
                # We construct a new dictionary, cleaning the rating value and adding the imdb_id
                # for each rating.
                value = re.match('(\d|\.)+', rating['Value']).group(0)
                ratings_data.append({'imdb_id': imdb_id, 'source': rating['Source'], 'value': value})

        # Finally, do a quick hack to ensure no rating contains the value 'N/A' which the OMDB API
        # sometimes returns.
        for rating in ratings_data:
            if rating['value'] == 'N/A':
                ratings_data.remove(rating)

        if len(ratings_data) == 0:
            return None

        return ratings_data
