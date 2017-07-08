import json
import os
import requests

try:
    OMDB_API = os.environ['API_KEY']
except KeyError:
    try:
        from GLOBALS import OMDB_API
    except ImportError:
        print("API is not known")
        exit()

# TODO Add genres table. Currently, we are deleting it in split_data.


class GetAPI(object):

    def __init__(self, api_key=OMDB_API):
        self.api_key = api_key
        self.source_topic = 'imdb_ids'
        self.destination_topic = 'omdb'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    def get_info(self, request):
        imdb_id = request['imdb_id']
        data = self.get_omdbapi_json(imdb_id)
        if data['Response'] == 'False':
            return None
        all_data = self.split_data(data, imdb_id)
        return all_data

    def get_omdbapi_json(self, imdb_id):
        html = requests.get('http://www.omdbapi.com/?i=' + imdb_id + '&apikey=' + self.api_key
                            , headers=self.headers)
        return json.loads(html.text)


    def lower_keys(self, dictionary):
        return dict((k.lower(), v) for k, v in dictionary.items())


    def split_data(self, api_data, imdb_id):

        api_data = self.lower_keys(api_data)
        bad_fields = [ 'response'
                      , 'season'
                      , 'totalseasons'
                      , 'seriesid'
                      , 'dvd'
                      , 'genre'
                      ]

        for i in bad_fields:
            try:
                del api_data[i]
            except:
                pass

        cast_data=[]
        if 'actors' in api_data.keys():
            for actor in api_data['actors'].split(','):
                cast_data.append({'name':actor.strip(), 'imdb_id':imdb_id, 'role':'actor'})
            del api_data['actors']

        crew_data=[]
        if 'director' in api_data.keys():
            for director in api_data['director'].split(','):
                crew_data.append({'name':director.strip(), 'imdb_id':imdb_id, 'role':'director'})
            del api_data['director']

        if 'writer' in api_data.keys():
            for writer in api_data['writer'].split(','):
                crew_data.append({'name':writer.strip(), 'imdb_id':imdb_id, 'role':'writer'})
            del api_data['writer']

        ratings_data=[]

        if 'metascore' in api_data.keys():
            ratings_data.append({'source':'metascore', 'imdb_id':imdb_id, 'value':api_data['metascore']})
            del api_data['metascore']
        ratings_data.append({'source':'imdb', 'imdb_id':imdb_id, 'value':api_data['imdbrating']})
        del api_data['imdbrating']
        if 'ratings' in api_data.keys():
            other_ratings = api_data['ratings']
            for rating in other_ratings:
                rating.update({'imdb_id': imdb_id})
                rating = self.lower_keys(rating)
                ratings_data.append(rating)
            del api_data['ratings']

        # We change the name of the key from imdbid to imdb_id
        # This is to conform to the structure in the rest of the apis
        # which allows for ease of testing.
        api_data["imdb_id"] = api_data["imdbid"]
        del api_data["imdbid"]
        main_data = [api_data]

        all_data = {'omdb_main':main_data, 'omdb_ratings':ratings_data, 'omdb_crew':crew_data, 'omdb_cast':cast_data}
        return all_data