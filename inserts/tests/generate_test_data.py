from apis.get_omdb import GetAPI as omdbAPI
from apis.get_tmdb import GetAPI as tmdbAPI
from apis.get_itunes import GetAPI as itunesAPI
from apis.get_youtube import GetAPI as youtubeAPI
import json


data = {'imdb_id':'tt2562232'}

omdb = omdbAPI()
data.update(omdb.get_info(data))

tmdb = tmdbAPI()
data.update(tmdb.get_info(data))

itunes = itunesAPI()
data.update(itunes.get_info(data))

youtube = youtubeAPI()
data.update(youtube.get_info(data))

with open('test_data.json', 'w') as outfile:
    json.dump(data, outfile)