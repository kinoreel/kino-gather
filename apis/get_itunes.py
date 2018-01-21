import requests
import json

from fuzzywuzzy import fuzz
from datetime import datetime


class GetAPI(object):
    """
    Top level class imported by kafka_apis.py.
    Gets and standardises the response from the iTunes API.
     The class also hold responsibility of the topic it consumes from and the topic it produces to.
    """

    def __init__(self):
        self.source_topic = 'trailer'
        self.destination_topic = 'itunes'

    def get_info(self, request):

        # Get information on film collected from upstream apis
        imdb_id, title, release_date, year = self.retrieve_data(request)

        data = RequestAPI().get_itunes(title)

        if data is None:
            return {'itunes_main': []}

        films = [iTunesFilm(imdb_id, e) for e in data]

        film = ChooseBest.get_best_match(films, title, release_date)

        if film is None or (film.main_data['hd_rental_price'] is None and film.main_data['rental_price'] is None):
            return {'itunes_main': []}

        return {'itunes_main': [film.main_data]}

    @staticmethod
    def retrieve_data(request):
        """
        Gets data from upstream apis needed for the retrieving the infrmation
        from the iTunes API.
        :param request: The data collected from upstream apis
        :return: Film info needed in the collection of a film from the iTunes api
        """
        imdb_id = request['imdb_id']
        title = request['tmdb_main'][0]['title']
        release_date = request['tmdb_main'][0]['release_date']
        year = release_date[0:4]
        return imdb_id, title, release_date, year


class RequestAPI(object):
    """This class requests data for a given imdb_id from the OMDB API."""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    def get_itunes(self, title):
        """
        Gets information for a movie from the iTunes API.
        :param title: The title of our film.
        :return: JSON of the itunes data.
        """
        title = title.replace(' ', '+')
        url = 'http://itunes.apple.com/search?term={0}&country=gb&media=movies&entity=movie'.format(title)
        html = requests.get(url)
        return json.loads(html.text)['results']


class iTunesFilm(object):
    """
    This class reconstructs the response returned from the iTunes API, for ease
    of accessing the data
    """

    def __init__(self, imdb_id, response):
        self.raw_response = response
        self.main_data = {'imdb_id': imdb_id,
                          'title': response['trackName'],
                          'url': response['trackViewUrl'].split('?')[0],
                          'released': self.fix_release_date(response['releaseDate']),
                          'hd_rental_price': response.get('trackHdRentalPrice'),
                          'rental_price': response.get('trackRentalPrice'),
                          'hd_purchase_price': response.get('trackHdPrice'),
                          'purchase_price': response.get('trackPrice')}

    @staticmethod
    def fix_release_date(release_date):
        """
        Gets date from the iTunes release timestamp.
        :param release_date: Date in the formatted by youtube - 2013-07-19T04:02:19.000Z
        :return: Duration in minutes
        """
        release_date = release_date.split('T')[0]
        return release_date

class ChooseBest(object):
    """
    This class compares each of the films returned by the iTunes API against
    the requested film and returns the best match.
    """

    @staticmethod
    def get_best_match(films, req_title, req_release_date):
        """
        Determines the film returned by the iTunes api that best matches the requested film
        :param films: List of iTunesFilm instances.
        :param req_title: The name of the title we requested
        :param req_release_date: The release date of the requested film
        :return: The film with the best match score, or None if no match score is greater than 85.
        """
        match_scores = [ChooseBest.get_match_score(e.main_data['title'], e.main_data['released'],
                                             req_title, req_release_date) for e in films]
        if len(match_scores) == 0:
            return None
        if max(match_scores) < 85:
            return None
        return films[match_scores.index(max(match_scores))]

    @staticmethod
    def get_match_score(title, release_date, requested_title, requested_release_date):
        """
        This returns a match score for a film returned by the YouTube API, constructed
        from the title score minus the runtime score.
        :param title: The title of the film returned by the YouTube API.
        :param requested_title: The title of the requested film.
        :return: A score out of 100.
        """
        title_score = ChooseBest.get_title_score(title, requested_title)
        release_date_score = ChooseBest.release_date_score(release_date, requested_release_date)
        match_score = title_score - release_date_score
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
    def release_date_score(release_date, requested_release_date):
        """
        This function checks that the published date - the date it was uploaded to
        the youtube channel - is not greater than the release date.
        :param requested_release_date: A date string in the form yyyymmdd
        :param release_date: A date string in the form yyyymmdd
        :return: Boolean - True if the published_date is greater than the release_date.
        False if the release_date is more recent.
        """
        release_date = datetime.strptime(release_date, '%Y-%m-%d')
        requested_release_date = datetime.strptime(requested_release_date, '%Y-%m-%d')
        days_diff = abs((requested_release_date - release_date).days)
        months_diff = round(days_diff/30,2)
        return months_diff
