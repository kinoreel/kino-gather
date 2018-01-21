import os
import re
from apiclient.discovery import build

from apis.GatherException import GatherException


try:
    YOUTUBE_FILMS_API = os.environ['API_KEY']
except KeyError:
    try:
        from apis.GLOBALS import YOUTUBE_FILMS_API
    except ImportError:
        print("API is not known")
        exit()


class GetAPI(object):
    """
    Top level class imported by kafka_apis.py.
    Gets and standardises data from YouTube api, searching for trailers
    The class also hold responsibility of the topic it consumes from and the topic it produces to.
    """
    def __init__(self):
        self.source_topic = 'tmdb'
        self.destination_topic = 'itunes'

    def get_info(self, request):

        # Get information on film collected from upstream apis
        imdb_id, title, suggested_video_id, release_date, year = self.retrieve_data(request)

        # Get the youtube api response for the video id provided by the tmdb api
        if suggested_video_id:
            response = YouTubeAPI().search_by_id(suggested_video_id)
            # We preference tmdb. Whilst quality tends to be better when
            # directly querying the YouTube api, we cannot guarantee
            # we return the trailer for the correct film.
            if response:
                # Return api data to kafka stream
                video = YouTubeVideo(imdb_id, response)
                return {'trailer_main': [video.main_data]}

        # If there was no response when searching for the tmdb trailer,
        # search YouTube for trailers
        string = '{0} ({1}) Trailer HD'.format(title, year)

        videos = [YouTubeVideo(imdb_id, e) for e in YouTubeAPI().search_by_string(string)]

        # Choose the best video
        best_video = ChooseBest().choose_best(videos)

        if best_video:
            return {'trailer_main': [best_video.main_data]}
        else:
            # If we could not find a trailer we can't do much
            # so throw an error to prevent further streaming.
            GatherException('Could not find a trailer')

    @staticmethod
    def retrieve_data(request):
        """
        Gets data from upstream apis needed for the retrieving the trailer
        for a film.
        :param request: The data collected from upstream apis
        :return: Film info needed in the collection of a film trailer from the YouTube api
        """
        imdb_id = request['imdb_id']
        title = request['tmdb_main'][0]['title']
        try:
            tmdb_trailer = request['tmdb_trailer'][0]['video_id']
        except IndexError:
            tmdb_trailer = None
        release_date = request['tmdb_main'][0]['release_date']
        year = release_date[0:4]
        return imdb_id, title, tmdb_trailer, release_date, year


class YouTubeAPI(object):
    """This class requests data for a given imdb_id from the YouTube API."""

    def __init__(self, api_key=YOUTUBE_FILMS_API):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def search_by_id(self, video_id):
        """
        This function searches YouTube API for our requested title using the
        function search_youtube. Then for each result, we request the content
        and statistics information.
        :param tmdb_trailer: The video id for the trailer provided by the TMDB api
        :return: A JSON object containing the response from the YouTube API.
        """
        response = self.youtube.videos().list(
            part='snippet',
            id=video_id,
        ).execute()
        try:
            response = response['items'][0]
        except IndexError:
            return
        response['video_id'] = video_id
        if response:
            response.update(self.get_content_details(video_id))
            response.update(self.get_stats(video_id))

        if Validate.validate(response):
            return response


    def search_by_string(self, string):
        """
        This function searches YouTube API for our requested title using the
        function search_youtube. Then for each result, we request the content
        and statistics information.
        :param title: The film we are requesting from the YouTube API.
        :param year: The year the requested film was released
        :return: A JSON object containing the response from the YouTube API.
        """
        response = self.youtube.search().list(
            part='snippet',
            regionCode='gb',
            q=string,
            type='video',
        ).execute()['items']
        for video in response:
            video_id = video['id']['videoId']
            video['video_id'] = video_id
            video.update(self.get_content_details(video_id))
            video.update(self.get_stats(video_id))

        response = [e for e in response if Validate.validate(e)]
        return response

    def get_content_details(self, video_id):
        """
        This function returns the content information - length, -
        for a particular video.
        :param video_id: The youtube video id.
        :return: A JSON object containing the response from youtube.
        """
        response = self.youtube.videos().list(
            part='contentDetails',
            id=video_id,
        ).execute()
        return response['items'][0]['contentDetails']

    def get_stats(self, video_id):
        """
        This function returns the stats information - likes, dislike, etc. -
        for a particular video.
        :param video_id: The youtube video id.
        :return: A JSON object containing the response from youtube.
        """
        response = self.youtube.videos().list(
            part='statistics',
            id=video_id
        ).execute()
        return response['items'][0]['statistics']


class Validate(object):
    """
    This class validates a YouTube video, ensuring that the video is still up, it is not
    regionally restricted, etc
    """

    @staticmethod
    def validate(response):
        if Validate.region(response['snippet']) and \
                Validate.title(response['snippet']) and \
                Validate.channel_title(response['snippet']) and \
                Validate.duration(response):
            return True
        return False

    @staticmethod
    def region(response):
        try:
            if 'GB' in response['regionRestriction']['blocked']:
                return False
        except KeyError:
            pass
        return True

    @staticmethod
    def title(response):
        bad_words = ['german', 'deutsch', 'spanish', 'españa', 'espana']
        for word in bad_words:
            if word in response['title'].lower():
                return False
        return True

    @staticmethod
    def channel_title(response):
        bad_channels = ['moviepilot trailer', 'diekinokritiker', '7even3hreetv', 'kilkenny1978', 'movieclips']
        for channel in bad_channels:
            if channel in response['channelTitle'].lower():
                return False
        return True

    @staticmethod
    def duration(response):
        """
        Checks that the video duration is between 1 and 6 minutes
        :param response: The length of the video
        """
        if 0 < int(Validate.fix_duration(response['duration'])) < 6:
            return True
        return False

    @staticmethod
    def fix_duration(duration):
        """
        Reformat youtube duration from PT1H59M15S into minutes
        :param duration: Time in the YouTube format - PT1H59M15S
        :return: Duration in minutes
        """
        runtime = duration.replace('PT', '')
        try:
            h = re.findall('\d{1,2}(?=H)', runtime)[0]
        except IndexError:
            h = 0
        try:
            m = re.findall('\d{1,2}(?=M)', runtime)[0]
        except IndexError:
            m = 0
        return str(int(h) * 60 + int(m))


class YouTubeVideo(object):
    """
    This class reconstructs the response returned from the YouTube API, making
    a new JSON object that is easier to handle for later applications.
    """
    def __init__(self, imdb_id, response):

        self.raw_response = response

        self.main_data = {
            'imdb_id': imdb_id,
            'title': response['snippet']['title'],
            'video_id': response['video_id'],
            'view_count': response.get('viewCount') or 0,
            'definition': response['definition'],
            'duration': Validate.fix_duration(response['duration']),
            'channel_title': response['snippet']['channelTitle'],
            'channel_id': response['snippet']['channelId'],
            'published_at': response['snippet']['publishedAt'].split('T')[0],
            'like_count': response.get('likeCount') or '0',
            'dislike_count':response.get('dislikeCount') or '0',
            'comment_count': response.get('comment_count') or '0'
        }


class ChooseBest(object):
    """
    This class compares each of the trailers returned by the YouTube API returns the best match.
    """
    @staticmethod
    def choose_best(videos):

        # Preference hd videos
        hd = ChooseBest.get_hd_videos(videos)
        if len(hd) > 0:
            videos = hd

        # sort by view count
        responses = ChooseBest.sort_by_view_count(videos)

        try:
            return responses[0]
        except IndexError:
            return None

    @staticmethod
    def get_hd_videos(videos):
        """Returns a list of hd videos"""
        return [e for e in videos if e.main_data['definition'] == 'hd']

    @staticmethod
    def sort_by_view_count( videos):
        """Sorts videos by view count"""
        return sorted(videos, key=lambda x: int(x.main_data['view_count']), reverse=True)
