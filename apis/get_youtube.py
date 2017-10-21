import os
import re
from fuzzywuzzy import fuzz
from apiclient.discovery import build
from datetime import datetime

try:
    YOUTUBE_FILMS_API = os.environ['API_KEY']
except KeyError:
    try:
        from apis.GLOBALS import YOUTUBE_FILMS_API
    except ImportError:
        print("API is not known")
        exit()


class GetAPI(object):

    def __init__(self):
        self.source_topic = 'itunes'
        self.destination_topic = 'youtube'
        self.get_data = RequestAPI().get_youtube
        self.standardise_data = StandardiseResponse().standardise
        self.choose_best = ChooseBest().get_best_match

    def get_info(self, request):
        imdb_id = request['imdb_id']
        # title - taken from omdb
        title = request['omdb_main'][0]['title']
        # runtime - taken from tmdb - int
        runtime = request['tmdb_main'][0]['runtime']
        # release date - taken from tmdb - yyyy-dd-mm
        release_date = request['tmdb_main'][0]['release_date']
        data = self.get_data(title)
        if data:
            data = self.standardise_data(imdb_id, data)
            data = self.choose_best(data, title, runtime, release_date)
            if data:
                return [{'youtube_main': data}]
        else:
            return None


class RequestAPI(object):
    """This class requests data for a given imdb_id from the YouTube API."""

    def __init__(self, api_key=YOUTUBE_FILMS_API):
        self.api_key = api_key
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def get_youtube(self, title):
        """
        This function searches YouTube API for our requested title using the
        function search_youtube. Then for each result, we request the content
        and statistics information.
        :param title: The film we are requesting from the YouTube API.
        :return: A JSON object containing the response from the YouTube API.
        """
        youtube_data = []
        response = self.search_youtube(title)
        # For each film we in the youtube response, we
        # request the content_details and statistics for the film, constructing
        # a new dictionary of this information. We append these dictionaries
        # to the array youtube_data.
        for film in response:
            video_id = film['id']['videoId']
            info = film['snippet']
            content_details = self.get_content_details(video_id)
            get_stats = self.get_stats(video_id)
            info.update(content_details)
            info.update(get_stats)
            info.update({'video_id': video_id})
            youtube_data.append(info)

        return youtube_data

    def search_youtube(self, title):
        """
        This function searches the youtube api for a specific film
        :param title: The film we are requesting from the youtube api.
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
        ).execute()
        return response['items']

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


class StandardiseResponse(object):
    """
    This class reconstructs the response returned from the YouTube API, making
    a new JSON object that is easier to handle for later applications.
    """

    def standardise(self, imdb_id, api_data):
        """
        We construct a new dictionary from teh API data, standardising the format
        so we it can be handled easily in later applications.
        :param imdb_id: The imdb_id for the film that was requested from OMDB API
        :param api_data: The raw response from teh OMDB API
        :return: A standardised dictionary.
        """
        main_data = []
        for film in api_data:
            standardised_film = self.get_main_data(imdb_id, film)
            main_data.append(standardised_film)
        return main_data

    def get_main_data(self, imdb_id, api_data):
        """
        Gets the main data returned by the YouTube API, and constructs a dictionary
        of this information. The api data is already pretty good, so we only have to change
        a few small things.
        :param imdb_id:
        :param api_data:
        :return:  A dictionary containing the main info for the film.
        """
        main_data = {
            'likeCount': api_data['likeCount'],
            'favoriteCount': api_data['favoriteCount'],
            'dislikeCount': api_data['dislikeCount'],
            'channelId': api_data['channelId'],
            'channelTitle': api_data['channelTitle'],
            'title': api_data['title'],
            'publishedAt': self.fix_published_date(api_data['publishedAt']),
            'duration': self.fix_runtime(api_data['duration']),
            'definition': api_data['definition'],
            'dimension': api_data['dimension'],
            'video_id': api_data['video_id'],
            'imdb_id': imdb_id,
            'regionRestriction': ','.join(api_data['regionRestriction']['allowed'])
        }
        return main_data

    def fix_runtime(self, runtime):
        """
        This function transforms the formatted time returned by youtube
        into a minutes.
        :param time: Time in the formatted by youtube - PT1H59M15S
        :return: Duration in minutes
        """
        runtime = re.sub('H|M', ':', runtime.replace('PT', '').replace('S', ''))
        h, m, s = runtime.split(':')
        return str(int(h) * 60 + int(m))

    def fix_published_date(self, published_date):
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

    def get_best_match(self, api_data, req_title, req_runtime, req_release_date):
        """
        This function determines the film returned by the YouTube
        API, that best matches the film requested.
        To do this we use compare the title and the runtime of the film.
        We then pull the best result based on this.
        :param api_data: The list of dictionaries containing movie data returned from teh YouTube API.
        :param req_title: The name of the title we requested
        :param req_runtime: The runtime of the
        :param req_release_date: The release date of the requested film
        :return: The film with the best match score, or None if no match score is greater than 85.
        """
        match_scores = [self.get_match_score(e['title'], e['duration'], req_title, req_runtime)
                        for e in api_data if self.check_published_date(e['publishedAt'], req_release_date)]
        if max(match_scores) > 85:
            return api_data[match_scores.index(max(match_scores))]
        else:
            return None

    def get_match_score(self, title, runtime, requested_title, requested_runtime):
        """
        This returns a match score for a film returned by the YouTube API, constructed
        from the title score minus the runtime score.
        :param title: The title of the film returned by the YouTube API.
        :param runtime: The runtime of the film returned by the YouTube API
        :param requested_title: The title of the requested film.
        :param requested_runtime: The runtime of the requested film.
        :return: A score out of 100.
        """
        title_score = self.get_title_score(title, requested_title)
        runtime_score = self.get_runtime_score(runtime, requested_runtime)
        match_score = title_score - runtime_score
        return match_score

    def get_title_score(self, title, requested_title):
        """
        This function provides a score for how closely the a film title
        matches the requested title.
        :param title: The title being compared.
        :param requested_title: The title was are comparing to.
        :return: An integer score between 0 and 100. Higher is better
        """
        title_score = fuzz.ratio(title.lower(), requested_title.lower())
        return title_score

    def get_runtime_score(self, runtime, requested_runtime):
        """
        This function provides a score for how closely the a file runtime
        matches the requested film runtime. Lower is better.
        :param title: The film runtime being compared.
        :param requested_title: The runtime was are comparing to.
        :return: An integer score
        """
        runtime_score = abs(int(runtime) - int(requested_runtime))
        return runtime_score

    def check_published_date(self, published_date, release_date):
        """
        This function checks that the published date - the date it was uploaded to
        the youtube channel - is not greater than the release date.
        :param published_date: A date string in the form yyyymmdd
        :param release_date: A date string in the form yyyymmdd
        :return: Boolean - True if the published_date is greater than the release_date.
        False if the release_date is more recent.
        """
        published_date = datetime.strptime(published_date, '%Y-%m-%d')
        release_date = datetime.strptime(release_date, '%Y-%m-%d')
        if (published_date-release_date).days > 0:
            return True
        else:
            return False
