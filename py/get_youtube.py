import re
#from fuzzywuzzy import fuzz
from apiclient.discovery import build

# TODO: Introduce fuzzy logic to ensure that the film returned matches the film we requested.
# TODO: There are additional statistic we can be grabbing - line 106


class GetYoutube:

    def __init__(self, api_key):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def get_info(self, imdb_id, title):
        data = self.search_youtube(title)
        youtube_main = [self.get_movie_info(imdb_id, title, data[0])]
        youtube_other = []
        for item in data[1:]:
            youtube_other.append(self.get_movie_info(imdb_id, title, item))

        all_data = {}
        #if fuzz.partial_ratio(youtube_main[0]['title'], title) > 85:
        if 1==1:
            all_data['youtube_films_main'] = youtube_main
            all_data['youtube_films_other'] = youtube_other
        else:
            youtube_other.extend(youtube_main)
            all_data['youtube_films_other'] = youtube_other
        return all_data

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
            q=title,
            type='video',
            videoDuration='long',
            videoType='movie'
        ).execute()
        return response['items']

    def fx_movie_item(self, data):
        movie = {}
        movie['title']=data['snippet']['title']
        movie['description']=data['snippet']['description']
        movie['video_id']=data['id']['videoId']
        movie['channel_title']=data['snippet']['channelTitle']
        movie['channel_id']=data['snippet']['channelId']
        movie['published']=data['snippet']['publishedAt']
        return movie

    def get_content_details(self, video_id):
        response = self.youtube.videos().list(
            part='contentDetails',
            id=video_id,
        ).execute()
        return response

    def fx_content_details(self, data):
        content_details={}
        if data['items'][0]['contentDetails']['licensedContent']:
            content_details['licenced']='licenced'
        else:
            content_details['licenced'] = 'not licenced'

        try:
            content_details['region']=','.join(data['items'][0]['contentDetails']['regionRestriction']['allowed'])
        except:
            content_details['region']=''

        content_details['dimension']=data['items'][0]['contentDetails']['dimension']
        content_details['caption']=data['items'][0]['contentDetails']['caption']
        content_details['duration']=self.fix_time(data['items'][0]['contentDetails']['duration'])
        content_details['definition']=data['items'][0]['contentDetails']['definition']
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
        stats['likes']=data['items'][0]['statistics'].get('likeCount')
        stats['dislikes']=data['items'][0]['statistics'].get('dislikeCount')
        stats['comments'] = data['items'][0]['statistics'].get('commentCount')
        return stats
