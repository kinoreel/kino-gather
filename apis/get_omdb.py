import json
import os
from apis.GatherException import GatherException

import requests

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
    This class gets, and standardises, the response from the OMDB API
    for a given imdb_id. The class also hold responsibility of the topic
    it consumes from and the topic it produces to.
    """

    def __init__(self):
        self.source_topic = 'imdb_ids'
        self.destination_topic = 'omdb'
        self.get_data = RequestAPI().get_omdb
        self.standardise_data = StandardiseResponse().standardise

    def get_info(self, request):
        imdb_id = request['imdb_id']
        data = self.get_data(imdb_id)
        if data is None:
            raise GatherException(imdb_id, 'No response from OMDB API')
        data = self.standardise_data(imdb_id, data)
        return data


class RequestAPI(object):
    """This class requests data for a given imdb_id from the OMDB API."""

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
            return None

class StandardiseResponse(object):
    """
    This class reconstructs the response returned from the OMDB API, making
    a new JSON object that is easier to handle for later applications.
    """

    def standardise(self, imdb_id, api_data):
        """
        We construct a new dictionary from teh API data, standardising the format
        so we it can be handled easily in later applications.
        :param imdb_id: The imdb_id for the film that was requested from OMDB API
        :param api_data: The raw response from the OMDB API
        :return: A standardised dictionary.
        """
        main_data = self.get_main_data(imdb_id, api_data)
        ratings_data = self.get_ratings_data(imdb_id, api_data)
        return {'omdb_main': main_data, 'omdb_ratings': ratings_data}

    def get_main_data(self, imdb_id, api_data):
        """
        Gets the main data returned by the OMDB API, and constructs a dictonary
        of this information.
        :param imdb_id: The imdb_id for the film we requested
        :param api_data: The OMDB API response
        :return: A single entry array containing the main info for the film.
        """
        try:
            main_data = [{'imdb_id': imdb_id,
                          'title': api_data['Title'],
                          'language': api_data['Language'],
                          'rated': api_data['Rated'],
                          'plot': api_data['Plot'],
                          'country': api_data['Country']
                          }]
        except:
            raise GatherException('No main data could be found from OMDB')
        return main_data

    def get_ratings_data(self, imdb_id, api_data):
        """
        Gets the rating data returned by the OMDB API, and creates an array of dictionaries
        detailing the ratings of the films. The ratings are not standardised in the OMDB output.
        Some are contained in the array 'Ratings', others - Metascore and IMDB - are displayed
        in the main branch of the response.
        There is no guarantee that any of rating information will be returned in the response.
        :param api_data: The OMDB API response
        :return: A array of dictionaries - imdb_id, source, value - for the film ratings
        """
        ratings_data = []

        if 'Metascore' in api_data.keys():
            ratings_data.append({'imdb_id': imdb_id, 'source': 'metascore', 'value': api_data['Metascore']})

        if 'imdbRating' in api_data.keys():
            ratings_data.append({'imdb_id': imdb_id, 'source': 'imdb', 'value': api_data['imdbRating']})

        if 'Ratings' in api_data.keys():
            for rating in api_data['Ratings']:
                # Each rating is already a dictionary containing two key values - Source and Value.
                # We construct a new dictionary for each rating.
                ratings_data.append({'imdb_id': imdb_id, 'source': rating['Source'], 'value': rating['Value']}  )

        # Finally, do a quick hack to ensure no rating contains the value 'N/A' which the OMDB API
        # sometimes returns.
        for rating in ratings_data:
            if rating['value'] == 'N/A':
                ratings_data.remove(rating)

        if len(ratings_data) == 0:
            raise GatherException('No ratings data could be found from OMDB')

        return ratings_data
