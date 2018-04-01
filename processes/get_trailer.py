import os
import re
from apiclient.discovery import build

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
    """
    Top level class imported by kafka_apis.py.
    Gets and standardises data from YouTube api, searching for trailers
    The class also hold responsibility of the topic it consumes from and the topic it produces to.
    """
    def __init__(self):
        self.source_topic = 'tmdb'
        self.destination_topic = 'trailer'

    def run(self, request):

        # Get information on film collected from upstream apis
        imdb_id, title, suggested_video_id, release_date, year = self.retrieve_data(request)

        # Get the youtube api response for the video id provided by the tmdb api
        if suggested_video_id:
            response = YouTubeAPI().search_by_id(suggested_video_id)
            # We preference tmdb. Whilst quality tends to be better when
            # directly querying the YouTube api, we cannot guarantee
            # we return the trailer for the correct film.
            if response:
                video = YouTubeVideo(imdb_id, response)
                # CHeck the title and duration
                if ChooseBest.check_title(video.main_data['title']) and video.main_data['duration'] < 300:
                    # Return api data to kafka stream
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
            raise GatherException(imdb_id, 'Could not find a trailer')

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

    def __init__(self, api_key=YOUTUBE_API_KEY):
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
        if 60 < int(Validate.fix_duration(response['duration'])) < 330:
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
            m = re.findall('\d{1,2}(?=M)', runtime)[0]
        except IndexError:
            m = 0
        try:
            s = re.findall('\d{1,2}(?=S)', runtime)[0]
        except IndexError:
            s = 0
        return int(m) * 60 + int(s)


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
            'view_count': self.parse_int(response.get('viewCount')),
            'definition': response['definition'],
            'duration': Validate.fix_duration(response['duration']),
            'channel_title': response['snippet']['channelTitle'],
            'channel_id': response['snippet']['channelId'],
            'published_at': response['snippet']['publishedAt'].split('T')[0],
            'like_count': self.parse_int(response.get('likeCount')),
            'dislike_count': self.parse_int(response.get('dislikeCount')),
            'comment_count': self.parse_int(response.get('commentCount'))
        }

    @staticmethod
    def parse_int(integer):
        """Changes string to integer, ignores errors"""
        try:
            return int(integer)
        except:
            return integer


class ChooseBest(object):
    """
    This class compares each of the trailers returned by the YouTube API returns the best match.
    """
    @staticmethod
    def choose_best(videos):

        for i in videos:
            print(i.main_data)

        # Remove videos with bad titles
        videos = [e for e in videos if ChooseBest.check_title(e.main_data['title'])]

        # Remove bad channels
        videos = [e for e in videos if ChooseBest.check_channel_id(e.main_data['channel_id'])]

        # Remove long videos
        videos = [e for e in videos if e.main_data['duration'] < 300]

        # Preference hd videos
        hd = ChooseBest.get_hd_videos(videos)
        if len(hd) > 0:
            videos = hd

        if len(videos) == 0:
            return None

        try:
            return videos[0]
        except IndexError:
            return None

    @staticmethod
    def get_hd_videos(videos):
        """Returns a list of hd videos"""
        return [e for e in videos if e.main_data['definition'] == 'hd']

    @staticmethod
    def check_channel_id(channelId):
        """
        Determines if channelId is from a channel that we do not want.
        :param videos: The YoutTUbe channel Id
        :return: Boolean - True if title is good, else False
        """
        bad_channels = ['UCzJd9BfQlXUVilNh0ewMt4Q',  # Trailers for interpretative dance films
                        'UCeWzte2dR3JMxhDgv-PWqTw',  # Not English
                        'UCTxYD92kxevI1I1-oITiQzg',  # Tv show trailers
                        'UCoviJXnjahw_A2vRGsSIL_w',  # Not English
                        ]
        for id in bad_channels:
            if id == channelId:
                return False
        return True

    @staticmethod
    def check_title(video_title):
        """
        Determines if title for trailer is acceptable.
        :param videos: The video title
        :return: Boolean - True if title is good, else False
        """
        bad_phrases = ['full movie']
        for phrase in bad_phrases:
            if phrase in video_title.lower():
                return False
        return True

    @staticmethod
    def sort_by_view_count( videos):
        """Sorts videos by view count"""
        return sorted(videos,
                      key=lambda x: (x.main_data['view_count'] is None, x.main_data['view_count']),
                      reverse=True)

if __name__=='__main__':
    a = Main()
    request = {'imdb_id': 'tt5221584',
               'tmdb_main': [{'title': 'Aquarius', 'runtime': 140, 'release_date': '2016-09-01'}],
               'tmdb_trailer':[{'video_id':'234235'}]}
    result = a.run(request)
    print(result)