import json
import os
import re

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
        if data['Response'] == 'True':
            data = self.standardise_data(imdb_id, data)
            return data
        else:
            return None


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
        return json.loads(html.text)


class StandardiseResponse(object):
    """
    This class reconstructs the response returned from the OMDB API, making
    a new JSON object that is easier to handle for later applications.
    """

    def __init__(self):
        # There are many fields returned by the OMDB_API that we do not care about.
        # We create a list of wanted fields that we will use in the function get_main_data
        self.fields = ['Title', 'Runtime', 'Language', 'Production', 'Rated', 'Poster',
                       'Plot', 'BoxOffice', 'Year', 'Released', 'Country']

    def standardise(self, imdb_id, api_data):
        main_data = self.get_main_data(imdb_id, api_data)
        cast_data = self.get_cast_data(imdb_id, api_data)
        crew_data = self.get_crew_data(imdb_id, api_data)
        ratings_data = self.get_ratings_data(imdb_id, api_data)
        return {'omdb_main': main_data, 'omdb_ratings': ratings_data, 'omdb_crew': crew_data, 'omdb_cast': cast_data}

    def get_main_data(self, imdb_id, api_data):
        """
        Gets the main data returned by the OMDB API, and constructs a dictonary
        of this information.
        :param imdb_id: The imdb_id for the film we requested
        :param api_data: The OMDB API response
        :return: A single entry array containing the main info for the film.
        """
        main_data = {'imdb_id': imdb_id}

        for field in self.fields:
            main_data.update({field.lower(): api_data[field]})

        return [main_data]

    def get_cast_data(self, imdb_id, api_data):
        """
        Gets the cast data returned by the OMDB API, and turns a comma
        separated string into an array of dictionaries
        There is no guarantee that any of cast information will be returned in the response.
        :param api_data: The OMDB API response
        :return: A array of dictionaries - imdb_id, name, role - for the cast in the film
        """
        cast_data = []
        if 'Actors' in api_data.keys():
            for actor in api_data['Actors'].split(','):
                cast_data.append({'name': actor.strip(), 'imdb_id': imdb_id, 'role': 'actor'})
        return cast_data

    def get_crew_data(self, imdb_id, api_data):
        """
        Gets the crew data returned by the OMDB API, and turns a number of comma
        separated string into an array of dictionaries
        There is no guarantee that any of crew information will be returned in the response.
        :param api_data: The OMDB API response
        :return: A array of dictionaries - imdb_id, name, actor - for the crew in the film
        """
        crew_data = []
        if 'Director' in api_data.keys():
            for director in api_data['Director'].split(','):
                name, spec = self.split_role_specification(director.strip())
                role = 'director'
                if spec != None:
                    role = role + ' ' + spec
                crew_data.append({'name': director.strip(), 'imdb_id': imdb_id, 'role': role})

        if 'Writer' in api_data.keys():
            for writer in api_data['Writer'].split(','):
                name, spec = self.split_role_specification(writer.strip())
                role = 'writer'
                if spec != None:
                    role = role+' '+spec
                crew_data.append({'name': name, 'imdb_id': imdb_id, 'role': role})

        return crew_data

    def split_role_specification(self, name):
        """
        This function removes any role specification from a crew members name.
        OMDB can specify more information on the role after a crew members name,
        for instance - 'Phillip K Dick (novel)' is returned rather than 'Phillip K Dick'.
        We want to remove these role specification from the and add them instead to the role.
        :param crew_name: The crew name -either writer or directory returned by the OMDB API.
        :return: The split name and role specification.
        """
        try:
            spec = re.search(r'\(.*\)', name).group(0)
            name = name.replace(spec, '').strip()
        # If we error on Attribute we know there is no specification attached to the name.
        except AttributeError:
            spec = None
        return name, spec


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

        return ratings_data
