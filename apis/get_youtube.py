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
        '''
        Thif function gets the movie info returned by the youtube_api
        :param request: A json object containing at least imdb_id, runtime and movie title info.
        :return: Film info returned by the youtube api.
        '''
        imdb_id = request['imdb_id']
        title = request['omdb_main'][0]['title']
        runtime = int(request['omdb_main'][0]['runtime'].replace(' min',''))
        data = self.search_youtube(title)
        # We check that we have successfully returned a result,
        # else we return the empty json.
        if data:
            standardised_data = []
            # We loop though the each response provided by the youtube api
            # expanding and standardising the information.
            for item in data:
                standardised_data.append(self.get_movie_info(imdb_id, title, item))
            # With our array of standardised information we then choose the film that
            # best matches the film we requested.
            youtube_main = self.get_best_film(standardised_data, title, runtime)
        else:
            youtube_main = self.empty_json

        return {'youtube_films_main': youtube_main}

    def search_youtube(self, title):
        '''
        This function searches the youtube api for a specific film
        :param title: The film we are requesting from the youtube api.
        :return: A json object containing the responses from youtube.
        '''
        response = self.youtube.search().list(
            part='snippet',
            regionCode='gb',
            q=title,
            type='video',
            videoDuration='long',
            videoType='movie'
        ).execute()
        return response['items']

    def get_movie_info(self, imdb_id, title, data):
        '''
        This function cleans and pulls additional information for each film returned
        by the initial response from the youtube api.
        Ths function works in three stages.
         - Standardise the response.
         - Get and standardise information on video content
         - Get and standardise information on video statistics
        :param imdb_id: The original imdb_id
        :param title: The original requested title
        :param data: The json response for a sinlge entry returned by the youtube api.
        :return: A standardised and extended json object containing information on the movie
        '''
        # Clean movie info
        movie_info = self.fx_movie_item(data)
        movie_info['imdb_id'] = imdb_id
        movie_info['orig_title'] = title
        video_id = movie_info['video_id']
        # Get and fix content info
        content = self.get_content_details(video_id)
        content = self.fx_content_details(content)
        movie_info.update(content)
        # Get and fix stats info.
        stats = self.get_stats(video_id)
        stats = self.fx_stats(stats)
        movie_info.update(stats)
        return movie_info

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
        content_details['duration'] = self.fix_runtime(data['items'][0]['contentDetails']['duration'])
        content_details['definition'] = data['items'][0]['contentDetails']['definition']
        return content_details

    def fix_runtime(self, runtime):
        '''
        This function transforms the formatted time returned by youtube
        into a minutes.
        :param time: Time in the formatted by youtube - PT1H59M15S
        :return: Duration in minutes
        '''
        runtime = re.sub('H|M', ':', runtime.replace('PT', '').replace('S', ''))
        h, m, s = runtime.split(':')
        return int(h)*60+int(m)

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


    def get_best_film(self, data, requested_title, requested_runtime ):
        '''
        This function determines the film returned by the Youtube
        API, that best matches the film requested.
        To do this we use compare the title and the runtime of the film.
        We then pull the best result based on this.
        :param cleaned_movie_data: The list of dictionaries containing movie data
        we want to compare
        :param requested_title: The name of the title we requested
        :param requested_runtime: The runtime of the
        :return:
        '''
        match_scores = []
        for i in data:
            match_scores.append(self.get_match_score(i['title'], i['duration'], requested_title, requested_runtime))

        if max(match_scores) > 85:
            index_of_best = match_scores.index(max(match_scores))
            return data[index_of_best]
        else:
            return self.empty_json

    def get_match_score(self, title, runtime, requested_title, requested_runtime, ):
        title_score = self.get_title_score(title, requested_title)
        runtime_score = self.get_runtime_score(runtime, requested_runtime)
        match_score = title_score - runtime_score
        return match_score

    def get_title_score(self, title, requested_title):
        '''
        This function provides a score for how closely the a film title
        matches the requested title.
        :param title: The title being compared.
        :param requested_title: The title was are comparing to.
        :return: An integer score between 0 and 100. Higher is better
        '''
        title_score = fuzz.ratio(title.lower(), requested_title.lower())
        return title_score

    def get_runtime_score(self, runtime, requested_runtime):
        '''
        This function provides a score for how closely the a file runtime
        matches the requested film runtime. Lower is better.
        :param title: The film runtime being compared.
        :param requested_title: The runtime was are comparing to.
        :return: An integer score
        '''
        runtime_score = abs(runtime - requested_runtime)
        return runtime_score
