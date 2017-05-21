import json
import requests

class GetOMDB(object):

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    def get_info(self, imdb_id):
        data = self.get_omdbapi_json(imdb_id)
        if data['Response'] == 'False':
            return None
        all_data = self.split_data(data, imdb_id)
        return all_data

    def get_omdbapi_json(self, imdb_id):
        html = requests.get('http://www.omdbapi.com/?i=' + imdb_id
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
                cast_data.append({'name':actor.strip(), 'imdbid':imdb_id, 'role':'actor'})
            del api_data['actors']

        crew_data=[]
        if 'director' in api_data.keys():
            for director in api_data['director'].split(','):
                crew_data.append({'name':director.strip(), 'imdbid':imdb_id, 'role':'director'})
            del api_data['director']

        if 'writer' in api_data.keys():
            for writer in api_data['writer'].split(','):
                crew_data.append({'name':writer.strip(), 'imdbid':imdb_id, 'role':'writer'})
            del api_data['writer']

        ratings_data=[]

        if 'metascore' in api_data.keys():
            ratings_data.append({'source':'metascore', 'imdbid':imdb_id, 'value':api_data['metascore']})
            del api_data['metascore']
        ratings_data.append({'source':'imdb', 'imdbid':imdb_id, 'value':api_data['imdbrating']})
        del api_data['imdbrating']
        if 'ratings' in api_data.keys():
            other_ratings = api_data['ratings']
            for rating in other_ratings:
                rating.update({'imdbid': imdb_id})
                rating = self.lower_keys(rating)
                ratings_data.append(rating)
            del api_data['ratings']

        main_data = [api_data]
        all_data = {'omdb_main':main_data, 'omdb_ratings':ratings_data, 'omdb_crew':crew_data, 'omdb_cast':cast_data}
        return all_data

if __name__=='__main__':
    get = GetOMDB()
    data = get.get_info('tt2562232')
    blah = data['omdb_ratings']
    print(blah)
    blah = data['omdb_main']
    print(blah)
    blah = data['omdb_crew']
    print(blah)
    blah = data['omdb_cast']
    print(blah)