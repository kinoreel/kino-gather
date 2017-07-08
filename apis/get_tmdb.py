import json
import os
import requests

try:
    TMDB_API = os.environ['API_KEY']
except KeyError:
    try:
        from GLOBALS import TMDB_API
    except ImportError:
        print("API is not known")
        exit()

"""
# TODO: create tables for trailers/changes/spoken_langauges/belongs to a collection on gather.kino@kino,
# then uncomment in split_data
"""


class GetAPI(object):

    def __init__(self, api_key=TMDB_API):
        self.api_key = api_key
        self.source_topic = 'omdb'
        self.destination_topic = 'tmdb'

    def get_info(self, request):
        imdb_id = request['imdb_id']
        data = self.get_tmdb_json(imdb_id)
        all_data = self.split_movie_data(imdb_id, data)
        return all_data

    def get_tmdb_json(self, imdb_id):

        request_url = "https://api.themoviedb.org/3/movie/" \
          + imdb_id + "?api_key=" + self.api_key

        request_url = request_url + "&append_to_response=alternative_titles" \
          + ",release_dates,credits,images,similar,translations,trailers," \
          + "videos,keywords,lists,changes"

        html = requests.get(request_url)
        return json.loads(html.text)

    def split_movie_data(self, imdb_id, api_data):
        cast_data = api_data["credits"]["cast"]
        crew_data = api_data["credits"]["crew"]
        genre_data = api_data["genres"]
        company_data = api_data["production_companies"]
        alternative_titles = api_data["alternative_titles"]["titles"]
        images_data = api_data["images"]["posters"]
        backdrops_data = api_data["images"]["backdrops"]
        similar_movies = api_data["similar"]["results"]
        translations = api_data["translations"]["translations"]
        videos = api_data["videos"]["results"]
        keywords = api_data["keywords"]["keywords"]
        lists = api_data["lists"]["results"]
        changes = api_data["changes"]["changes"]
        trailers = api_data["trailers"]["youtube"]
        release_dates = api_data["release_dates"]["results"][0]["release_dates"]

        for i in cast_data:
            i["order_of_appearance"] = i["order"]
            del i["order"]

        del api_data["credits"]
        del api_data["release_dates"]
        del api_data["genres"]
        del api_data["production_companies"]
        del api_data["production_countries"]
        del api_data["alternative_titles"]
        del api_data["images"]
        del api_data["translations"]
        del api_data["videos"]
        del api_data["similar"]
        del api_data["keywords"]
        del api_data["lists"]
        del api_data["changes"]
        del api_data["trailers"]
        #TODO We actually want data for spoken languages and belongs_to_collection, but they are dictionaries.
        del api_data['spoken_languages']
        del api_data['belongs_to_collection']
        main_data = [api_data]

        all_data = {"tmdb_companies":company_data,
                    "tmdb_cast":cast_data,
                    "tmdb_crew":crew_data,
                    "tmdb_main":main_data,
                    "tmdb_genres":genre_data,
                    "tmdb_alternative_titles":alternative_titles,
                    "tmdb_posters":images_data,
                    "tmdb_similar":similar_movies,
                    "tmdb_translations":translations,
                    "tmdb_videos":videos,
                    #"tmdb_changes":changes,
                    "tmdb_lists":lists,
                    "tmdb_keywords":keywords,
                    "tmdb_backdrops":backdrops_data,
                    #"tmdb_trailers":trailers,
                    "tmdb_release_dates":release_dates
                    }

        for data_type, jlist in all_data.items():
            if data_type != "tmdb_main":
                for item in jlist:
                    item["imdb_id"] = imdb_id

        del all_data['tmdb_alternative_titles']
        del all_data['tmdb_posters']
        del all_data['tmdb_translations']
        del all_data['tmdb_lists']
        del all_data['tmdb_backdrops']
        del all_data['tmdb_release_dates']


        return all_data