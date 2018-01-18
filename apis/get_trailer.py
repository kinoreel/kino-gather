import os
import re
from dateutil.relativedelta import relativedelta
from apiclient.discovery import build
from datetime import datetime

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
        imdb_id, title, tmdb_trailer, release_date, year = self.retrieve_data(request)

        tmdb_trailer_data = self.get_tmdb_trailer_data(tmdb_trailer)

        if tmdb_trailer_data:
            data = StandardisedResponse.get_main_data(imdb_id, tmdb_trailer_data)
            return {'trailer_main': data}

        data = RequestAPI().get_trailers(title, year)
        responses = [StandardisedResponse.get_main_data(imdb_id, e) for e in data]
        best_response = ChooseBest().choose_best(responses, release_date, title)

        if best_response is None:
            main_data = None
        else:
            main_data = [{'imdb_id': imdb_id,
                          'video_id': best_response.main_data['video_id'],
                          'definition': best_response.main_data['definition'],
                          'channel_title': best_response.main_data['channelTitle'],
                          'channel_id': best_response.main_data['channelId']}]
        return {'trailer_main': main_data}

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

    @staticmethod
    def get_tmdb_trailer_data(tmdb_trailer):
        response = RequestAPI().get_tmdb_trailer(tmdb_trailer)
        if response and ValidateVideo.validate(response):
            return response
        return None


class RequestAPI(object):
    """This class requests data for a given imdb_id from the YouTube API."""

    def __init__(self, api_key=YOUTUBE_FILMS_API):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def get_trailers(self, title, year):
        """
        This function searches YouTube API for our requested title using the
        function search_youtube. Then for each result, we request the content
        and statistics information.
        :param title: The film we are requesting from the YouTube API.
        :param year: The year the requested film was released
        :return: A JSON object containing the response from the YouTube API.
        """
        search_string = '{0} ({1}) Trailer HD'.format(title, year)
        response = self.search_youtube_by_string(search_string)

        youtube_data = []
        for video in response:
            video_id = video['id']['videoId']
            additional_info = self.get_additional_info(video_id)
            video.update(additional_info)
            youtube_data.append(video)

        return youtube_data

    def get_tmdb_trailer(self, tmdb_trailer):
        """
        This function searches YouTube API for our requested title using the
        function search_youtube. Then for each result, we request the content
        and statistics information.
        :param tmdb_trailer: The video id for the trailer provided by the TMDB api
        :return: A JSON object containing the response from the YouTube API.
        """
        response = self.search_youtube_by_id(tmdb_trailer)
        if response:
            additional_info = self.get_additional_info(tmdb_trailer)
            response.update(additional_info)
        return response

    def search_youtube_by_string(self, search_string):
        """
        This function searches the youtube api for a specific film
        :param search_string: The search string
        :return: A JSON object containing the responses from youtube.
        """
        # We specify a number of parameters to ensure we
        # only receive movies that are accessible from a british regional code.
        response = self.youtube.search().list(
            part='snippet',
            regionCode='gb',
            q=search_string,
            type='video',
        ).execute()
        return response['items']

    def search_youtube_by_id(self, video_id):
        """
        This function returns the content information - length, -
        for a particular video.
        :param video_id: The youtube video id.
        :return: A JSON object containing the response from youtube.
        """
        response = self.youtube.videos().list(
            part='snippet',
            id=video_id,
        ).execute()
        try:
            return response['items'][0]['snippet']
        except TypeError:
            return None

    def get_additional_info(self, video_id):
        info = {}
        content_details = self.get_content_details(video_id)
        stats = self.get_stats(video_id)
        info.update(content_details)
        info.update(stats)
        info.update({'video_id': video_id})
        return info

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


class ValidateVideo(object):
    """
    This class validates a YouTube video, ensuring that the video is still up, it is not
    regionally restricted, etc
    """

    @staticmethod
    def validate(video):
        if ValidateVideo.check_region(video) and \
                ValidateVideo.check_title(video) and \
                ValidateVideo.check_channel_title(video):
            return True
        return False

    @staticmethod
    def check_region(video):
        try:
            if 'GB' in video['regionRestriction']['blocked']:
                return False
            return True
        except KeyError:
            return True

    @staticmethod
    def check_title(video):
        bad_words = ['german', 'deutsch', 'spanish', 'españa', 'espana']
        for word in bad_words:
            if word in video['title'].lower():
                return False
        return True

    @staticmethod
    def check_channel_title(video):
        bad_channels = ['moviepilot trailer', 'diekinokritiker', '7even3hreetv', 'kilkenny1978']
        for channel in bad_channels:
            if channel in video['channelTitle'].lower():
                return False
        return True


class StandardisedResponse(object):
    """
    This class reconstructs the response returned from the YouTube API, making
    a new JSON object that is easier to handle for later applications.
    """

    @staticmethod
    def get_main_data(imdb_id, api_data):
        """
        Extracts the relevant information for comparing trailers
        :return: A dictionary containing the relevant information
        """
        return {'imdb_id': imdb_id,
                'title': api_data['title'],
                'video_id': api_data['video_id'],
                'viewCount': api_data.get('viewCount') or 0,
                'definition': api_data['definition'],
                'duration': api_data['duration'],
                'channelTitle': api_data['channelTitle'],
                'channelId': api_data['channelId'],
                'publishedAt': api_data['publishedAt'].split('T')[0]
                }

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
        except:
            m = 0
        return str(int(h) * 60 + int(m))


class ChooseBest(object):
    """
    This class compares each of the trailers returned by the YouTube API returns the best match.
    """
    def choose_best(self, responses, release_date, movie_title):
        # Remove videos without a reasonable duration
        responses = [e for e in responses if self.check_duration(e.main_data['duration'])]
        # Remove videos that were published to early
        responses = [e for e in responses if self.check_published_date(e.main_data['publishedAt'], release_date)]
        # Check title
        responses = [e for e in responses if self.check_title(e.main_data['title'], movie_title)]
        hd = [e for e in responses if e.main_data['definition'] == 'hd']
        if len(hd) > 0:
            responses = hd
        # sort by view count
        responses = sorted(responses, key=lambda x: int(x.main_data.get('viewCount')), reverse=True)
        try:
            return responses[0]
        except IndexError:
            return None

    @staticmethod
    def check_duration(duration):
        """
        Checks that the video duration is between 1 and 6 minutes
        :param duration: The length of the video
        """
        if 0 < int(StandardisedResponse.fix_duration(duration)) < 6:
            return True
        return False

    @staticmethod
    def check_published_date(published_date, release_date):
        """
        Checks that the youtube video was not published
        more than to years before the release date.
        :param published_date: Youtube video published date - yyyy-mm-dd
        :param release_date: Release date of the movie - yyyy-mm-dd
        """
        earliest_reasonable_publish_date = datetime.strptime(release_date, '%Y-%m-%d') - relativedelta(years=2)
        published_date = datetime.strptime(published_date, '%Y-%m-%d')
        if (published_date-earliest_reasonable_publish_date).days > 0:
            return True
        return False

    @staticmethod
    def check_title(video_title, movie_title):
        """
        Checks that the youtube video has a reasonable title, containing the film
        title and the word 'trailer'.
        :param video_title: Title of the YouTube video
        :param movie_title: Title of the movie
        """
        bad_words = ['German', 'Deuthch']
        for word in bad_words:
            if word in video_title.lower():
                return False
        if movie_title.lower() in video_title.lower() and 'trailer' in video_title.lower():
            return True
        return False





