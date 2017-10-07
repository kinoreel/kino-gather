import os
import re
from fuzzywuzzy import fuzz
from apiclient.discovery import build

try:
    YOUTUBE_FILMS_API = os.environ['API_KEY']
except KeyError:
    try:
        from GLOBALS import YOUTUBE_FILMS_API
    except ImportError:
        print("API is not known")
        exit()

class GetAPI(object):

    def __init__(self, api_key=YOUTUBE_FILMS_API):
        self.api_key = api_key
        self.source_topic = 'itunes'
        self.destination_topic = 'youtube'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.empty_json = {}

    def get_info(self, request):
        imdb_id = request['imdb_id']
        title = request['omdb_main'][0]['title']
        runtime = int(request['omdb_main'][0]['runtime'].replace(' min',''))
        data = self.search_youtube(title)
        all_data = {}
        # We check that we have successfully returned a result,
        # else we return the empty json.
        if data:
            clean_data = []
            for item in data:
                clean_data.append(self.get_movie_info(imdb_id, title, item))
            youtube_main = [self.get_youtube_main(clean_data, title, runtime)]
        else:
            youtube_main = self.empty_json

        return {'youtube_films_main': youtube_main}

    def get_youtube_main(self, clean_data, requested_title, requested_runtime ):
        '''
        This function determine the film returned by the Youtube
        API, that best matches the film requested.
        To do this we use compare the title and the runtime of the film.
        We then pull the best result based on this.
        :param cleaned_movie_data: The list of dictionaries containing movie data
        we want to compare
        :param requested_title: The name of the title we requested
        :param requested_runtime: The runtime of the
        :return:
        '''
        # We determine the title scores by a fuzzy comparison of the titles to the requested title.
        # Higher is better.
        title_scores = [fuzz.ratio(e['title'], requested_title.lower()) for e in clean_data ]
        # We determine the runtime score by the absolute difference between runtimes to the requested runtimes.
        # Lower is better.
        runtime_scores = [abs(self.get_minutes(e['duration']) - requested_runtime) for e in clean_data ]
        # We determine the match score as the title_score minus the runtime_score.
        match_scores = [x - y for (x, y) in zip(title_scores, runtime_scores)]
        # If the max match_score is greater than 85, we return the corresponding data for that score,
        # else we return the empty json
        if max(match_scores) > 85:
            index_of_best = match_scores.index(max(match_scores))
            return clean_data[index_of_best]
        else:
            return self.empty_json


    def get_minutes(self, runtime):
        '''
        This function transforms a time string in the form HH:MI:SS into
        minutes.
        :param runtime: A time duration in the form HH:MI:SS
        :return: The corresponding time duration in minutes.
        '''
        h,m,s = runtime.split(':')
        return int(h)*60+int(m)

    def get_movie_info(self, imdb_id, title, data):
        movie_info = self.fx_movie_item(data)
        movie_info['imdb_id'] = imdb_id
        movie_info['orig_title'] = title
        video_id = movie_info['video_id']
        content = self.get_content_details(video_id)
        content = self.fx_content_details(content)
        movie_info.update(content)
        stats = self.get_stats(video_id)
        stats = self.fx_stats(stats)
        movie_info.update(stats)
        return movie_info

    def search_youtube(self, title):
        response = self.youtube.search().list(
            part='snippet',
            regionCode='gb',
            q=title,
            type='video',
            videoDuration='long',
            videoType='movie'
        ).execute()
        return response['items']

    def fx_movie_item(self, data):
        movie = {}
        movie['title'] = data['snippet']['title']
        movie['description'] = data['snippet']['description']
        movie['video_id'] = data['id']['videoId']
        movie['channel_title'] = data['snippet']['channelTitle']
        movie['channel_id'] = data['snippet']['channelId']
        movie['published'] = data['snippet']['publishedAt']
        return movie

    def get_content_details(self, video_id):
        response = self.youtube.videos().list(
            part='contentDetails',
            id=video_id,
        ).execute()
        return response

    def fx_content_details(self, data):
        content_details = {}
        if data['items'][0]['contentDetails']['licensedContent']:
            content_details['licenced'] = 'licenced'
        else:
            content_details['licenced'] = 'not licenced'

        try:
            content_details['region'] = ','.join(data['items'][0]['contentDetails']['regionRestriction']['allowed'])
        except:
            content_details['region'] = ''

        content_details['dimension'] = data['items'][0]['contentDetails']['dimension']
        content_details['caption'] = data['items'][0]['contentDetails']['caption']
        content_details['duration'] = self.fix_time(data['items'][0]['contentDetails']['duration'])
        content_details['definition'] = data['items'][0]['contentDetails']['definition']
        return content_details

    def fix_time(self, time):
        return re.sub('H|M', ':', time.replace('PT', '').replace('S', ''))

    def get_stats(self, video_id):
        response = self.youtube.videos().list(
            part='statistics',
            id=video_id
        ).execute()
        return response

    def fx_stats(self, data):
        stats={}
        stats['likes'] = data['items'][0]['statistics'].get('likeCount')
        stats['dislikes'] = data['items'][0]['statistics'].get('dislikeCount')
        stats['comments'] = data['items'][0]['statistics'].get('commentCount')
        return stats
