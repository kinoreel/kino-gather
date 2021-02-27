import os
import re
from fuzzywuzzy import fuzz
from apiclient.discovery import build
from datetime import datetime

from processes.gather_exception import GatherException

try:
    YOUTUBE_API_KEY = os.environ['YOUTUBE_API_KEY']
except KeyError:
    try:
        from processes.GLOBALS import YOUTUBE_API_KEY
    except ImportError:
        print("No API key provided")
        exit()


class Main(object):

    def __init__(self):
        self.source_topic = 'amazon'
        self.destination_topic = 'youtube'

    def run(self, request):

        # Get information on film collected from upstream apis
        imdb_id, title, release_date, year, runtime, has_other_stream = self.retrieve_data(request)

        # Search youtube for film
        response = RequestAPI().get_youtube(title)

        # If there is no response and we have not collected any
        # other streams from upstream apis, then raise an error
        # to prevent any further processing of record.
        # if response is None and not has_other_stream:
        #     raise GatherException(imdb_id, 'No streams found')

        # Create YouTubeFilm instances from the response from the api
        films = [YouTubeFilm(imdb_id, e) for e in response]

        # Compare each film returned by the YouTube api, to determine the best
        # match.
        film = ChooseBest.get_best_match(films, title, runtime, release_date)

        # If there are no good matches, and we have not collected any
        # other streams from upstream apis, then raise an error
        # to prevent any further processing of record.
        # if film is None and not has_other_stream:
        #     raise GatherException(imdb_id, 'No streams found')

        # If there are no good matches, but we have collected a stream from
        # an upstream api, then we want to continue processing the records, but
        # return nothing for the YouTube api
        if film is None:
            return {'youtube_main': []}

        return {'youtube_main': [film.main_data]}

    @staticmethod
    def retrieve_data(request):
        """
        Gets data from upstream apis needed for the retrieving the information
        from the YouTube API.
        :param request: The data collected from upstream apis
        :return: Film info needed in the collection of a film from the YouTube api
        """
        imdb_id = request['imdb_id']
        title = request['tmdb_main'][0]['title']
        release_date = request['tmdb_main'][0]['release_date']
        runtime = request['tmdb_main'][0]['runtime']
        year = release_date[0:4]
        has_other_stream = True
        if request['itunes_main'] == [] and request['amazon_main'] == []:
            has_other_stream = False
        return imdb_id, title, release_date, year, runtime, has_other_stream



class RequestAPI(object):
    """This class requests data for a given imdb_id from the YouTube API."""

    def __init__(self, api_key=YOUTUBE_API_KEY, http=None):
        self.api_key = api_key
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/39.0.2171.95 Safari/537.36'}
        self.youtube = build('youtube', 'v3', http=http, developerKey=api_key)

    def get_youtube(self, title, search_http=None, content_details_http=None, stats_http=None):
        """
        This function searches YouTube API for our requested title using the
        function search_youtube. Then for each result, we request the content
        and statistics information.
        :param title: The film we are requesting from the YouTube API.
        :param search_http: Needed in mocking the response of the api.
        :param content_details_http: Needed in mocking the response of the api.
        :param stats_http: Needed in mocking the response of the api.
        :return: A JSON object containing the response from the YouTube API.
        """
        youtube_data = []
        response = self.search_youtube(title, http=search_http)
        # For each film we in the youtube response, we
        # request the content_details and statistics for the film, constructing
        # a new dictionary of this information. We append these dictionaries
        # to the array youtube_data.
        for film in response:
            video_id = film['id']['videoId']
            info = film['snippet']
            # content_details = self.get_content_details(video_id, http=content_details_http)
            video_stats = self.get_stats(video_id, http=stats_http)
            info.update(video_stats['items'][0]['contentDetails'])
            info.update(video_stats['items'][0]['statistics'])
            info.update({'video_id': video_id})
            youtube_data.append(info)

        return youtube_data

    def search_youtube(self, title, http=None):
        """
        This function searches the youtube api for a specific film
        :param title: The film we are requesting from the youtube api.
        :param http: Needed in mocking the response of the api.
        :return: A JSON object containing the responses from youtube.
        """
        # We specify a number of parameters to ensure we
        # only receive movies that are accessible from a british regional code.
        response = self.youtube.search().list(
            part='snippet',
            regionCode='gb',
            q=title,
            type='video',
            videoDuration='long',
            videoType='movie'
        ).execute(http=http)
        return response['items']

    def get_content_details(self, video_id, http=None):
        """
        This function returns the content information - length, -
        for a particular video.
        :param video_id: The youtube video id.
        :param http: Needed in mocking the response of the api.
        :return: A JSON object containing the response from youtube.
        """
        response = self.youtube.videos().list(
            part='contentDetails',
            id=video_id,
        ).execute(http=http)
        return response['items'][0]['contentDetails']

    def get_stats(self, video_id, http=None):
        """
        This function returns the stats information - likes, dislike, etc. -
        for a particular video.
        :param video_id: The youtube video id.
        :param http: Needed in mocking the response of the api.
        :return: A JSON object containing the response from youtube.
        """
        return self.youtube.videos().list(
            part=['statistics', 'contentDetails'],
            id=video_id
        ).execute(http=http)


class YouTubeFilm(object):
    """
    This class creates a response object that allows us to easily
    retrieve the response returned from the YouTube API
    """

    def __init__(self, imdb_id, response):
        self.main_data = {
            'likeCount': response.get('likeCount'),
            'favoriteCount': response.get('favoriteCount'),
            'dislikeCount': response.get('dislikeCount'),
            'channelId': response['channelId'],
            'channelTitle': response['channelTitle'],
            'title': self.fix_title(response['title']),
            'publishedAt': self.fix_published_date(response['publishedAt']),
            'duration': self.fix_runtime(response['duration']),
            'definition': response['definition'],
            'dimension': response['dimension'],
            'video_id': response['video_id'],
            'imdb_id': imdb_id,
            'regionRestriction': self.get_region_restriction(response)
        }

    @staticmethod
    def get_region_restriction(response):
        """
        This function returns region restriction for a film.
        The region restriction is only provided when the content is licenced.
        :return: The regions that are able to watch the video.
        """
        try:
            region_data = response['regionRestriction']['allowed']
            # Need to sort for testing.
            region_data.sort()
            return ','.join(region_data)
        except KeyError:
            return None

    @staticmethod
    def fix_title(title):
        """
        Edits the title, to increase the chances of a match
        :param title: A movie title
        :return: A fixed move title
        """
        title = re.sub( '\((1|2)(0|9)\d{1,2}\)', '', title)
        title = title.replace('(Subbed)', '')
        title = title.strip()
        return title

    @staticmethod
    def fix_runtime(runtime):
        """
        This function transforms the formatted time returned by youtube
        into a minutes.
        :param time: Time in the formatted by youtube - PT1H59M15S
        :return: Duration in minutes
        """
        runtime = runtime.replace('PT', '')
        try:
            h = re.findall('\d{1,2}(?=H)', runtime)[0]
        except IndexError:
            h = 0
        try:
            m = re.findall('\d{1,2}(?=M)', runtime)[0]
        except:
            m = 0
        return str(int(h) * 60 + int(m))

    @staticmethod
    def fix_published_date(published_date):
        """
        This function transforms the formatted date returned by youtube
        into a string with the format 'yyyymmdd'.
        :param published_date: Date in the formatted by youtube - 2013-07-19T04:02:19.000Z
        :return: Duration in minutes
        """
        # get the date
        published_date = published_date.split('T')[0]
        return published_date


class ChooseBest(object):
    """
    This class compares each of the films returned by the YouTube API against
    the requested film and returns the best match.
    """

    @staticmethod
    def get_best_match(films, req_title, req_runtime, req_release_date):
        """
        This function determines the film returned by the YouTube
        API, that best matches the film requested.
        To do this we use compare the title and the runtime of the film.
        We then pull the best result based on this.
        :param films: The list YouTubeFilm instances
        :param req_title: The name of the title we requested
        :param req_runtime: The runtime of the
        :param req_release_date: The release date of the requested film
        :return: The film with the best match score, or None if no match score is greater than 85.
        """
        match_scores = [ChooseBest.get_match_score(e.main_data['channelId'],
                                                   e.main_data['title'],
                                                   e.main_data['duration'],
                                                   req_title,
                                                   req_runtime)
                        for e in films]
        if len(match_scores) == 0:
            return None
        if max(match_scores) < 85:
            return None

        return films[match_scores.index(max(match_scores))]

    @staticmethod
    def get_match_score(channel_id, title, runtime, requested_title, requested_runtime):
        """
        This returns a match score for a film returned by the YouTube API, constructed
        from the title score minus the runtime score.
        :param channel_id: The id of the video channel
        :param title: The title of the film returned by the YouTube API.
        :param runtime: The runtime of the film returned by the YouTube API
        :param requested_title: The title of the requested film.
        :param requested_runtime: The runtime of the requested film.
        :return: A score out of 100.
        """
        accepted_channels = [
            'UCigibLQE1B6tc4Itxj7p5FA',
        ]
        if channel_id in accepted_channels: return 100

        title_score = ChooseBest.get_title_score(title, requested_title)
        runtime_score = ChooseBest.get_runtime_score(runtime, requested_runtime)
        match_score = title_score - (runtime_score)
        return match_score

    @staticmethod
    def get_title_score(title, requested_title):
        """
        This function provides a score for how closely the a film title
        matches the requested title.
        :param title: The title being compared.
        :param requested_title: The title was are comparing to.
        :return: An integer score between 0 and 100. Higher is better
        """
        title_score = fuzz.ratio(title.lower(), requested_title.lower())
        return title_score

    @staticmethod
    def get_runtime_score(runtime, requested_runtime):
        """
        This function provides a score for how closely the a file runtime
        matches the requested film runtime. Lower is better.
        :param runtime: The film runtime being compared.
        :param requested_runtime: The runtime was are comparing to.
        :return: An integer score
        """
        runtime_score = abs(int(runtime) - int(requested_runtime))
        return runtime_score

    @staticmethod
    def get_release_date_score(upload_date, requested_release_date):
        """
        This function calculates the release_date score.
        If the video was uploaded before the film was released
        we take 100 away from match_score.
        :param upload_date: A date string in the form yyyymmdd
        :param requested_release_date: A date string in the form yyyymmdd
        :return: Boolean - True if the published_date is greater than the release_date.
        False if the release_date is more recent.
        """
        upload_date = datetime.strptime(upload_date, '%Y-%m-%d')
        requested_release_date = datetime.strptime(requested_release_date, '%Y-%m-%d')
        days = (upload_date-requested_release_date).days
        if days < 0:
            return abs(round(days/30))
        return 0
