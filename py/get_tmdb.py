import json
import requests

class GetTMDB(object):

    def __init__(self, api_key):
        self.api_key = api_key

    def get_tmdb_json(self, id):

        request_url = "https://api.themoviedb.org/3/movie/" \
          + id + "?api_key=" + api_key

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
        alternate_languages = api_data["translations"]["translations"]
        videos = api_data["videos"]["results"]
        keywords = api_data["kewords"]["keywords"]
        lists = api_data["lists"]["results"]
        changes = api_data["changes"]["changes"]
        trailers = api_data["trailers"]["youtube"]
        release_dates = api_data["release_dates"]["results"]

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
        main_data = [api_data]

        all_data = {"tmdb_companies":company_data,
                    "tmdb_cast":cast_data,
                    "tmdb_crew":crew_data,
                    "tmdb_main":main_data,
                    "tmdb_genre":genre_data,
                    "tmdb_alternative_titles":alternative_titles,
                    "tmdb_posters":images_data,
                    "tmdb_similar_movies":similar_movies,
                    "tmdb_alternate_languages":alternate_languages,
                    "tmdb_videos":videos,
                    "tmdb_changes":changes,
                    "tmdb_lists":lists,
                    "tmdb_keywords":keywords,
                    "tmdb_backdrops":backdrops_data,
                    "tmdb_trailers":trailers,
                    "tmdb_release_dates":release_dates}

        for data_type, jlist in all_data.iteritems():
            if data_type <> "tmdb_main":
                for item in jlist:
                    item["imdb_id"] = imdb_id

        return all_data


   def get_info(self, imdb_id):

       jdata = self.get_tmdb_json(imdb_id)
       all_data = self.split_movie_data(jdata)
       return all_data
