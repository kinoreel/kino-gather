import json
import re

import requests

from processes.gather_exception import GatherException


class Omdb:

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }

    def run(self, request: dict):
        imdb_id = request['imdb_id']
        response = self.get_omdb(imdb_id)
        data = self.format_response(imdb_id, response)
        return data

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

    def format_response(self, imdb_id, api_data):
        """
        Constructs a new dictionary from the API data.
        :param imdb_id: The imdb_id for the requested film
        :param api_data: The raw response from the OMDB API
        :return: A standardised dictionary.
        """
        main_data = self.get_main_data(imdb_id, api_data)
        ratings_data = self.get_ratings_data(imdb_id, api_data)
        if ratings_data is None:
            GatherException(imdb_id, 'OMDB cannot find ratings for film')
        if main_data is None:
            GatherException(imdb_id, 'OMDB cannot find ratings for film')
        return {'omdb_main': main_data, 'omdb_ratings': ratings_data}

    def get_main_data(self, imdb_id, api_data):
        """
        Gets the main data returned by the OMDB API, and constructs a dictionary
        of this information.
        :param imdb_id: The imdb_id for the requested film
        :param api_data: The raw response from the OMDB API.
        :return: A dictionary containing the main data from the OMDB api
        """
        if api_data.get('Genre') == 'Short':
            raise GatherException(imdb_id, 'OMDB states that this film is a short film')
        try:
            main_data = [{
                'imdb_id': imdb_id,
                'title': api_data['Title'],
                'language': api_data['Language'],
                'rated': api_data['Rated'].replace('N/A', '').replace('NOT RATED', '').replace('UNRATED', ''),
                'plot': api_data['Plot'],
                'country': api_data['Country']
            }]
        except KeyError:
            raise GatherException('No main data could be found from OMDB')
        return main_data

    def get_ratings_data(self, imdb_id, api_data):
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
