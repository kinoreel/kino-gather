import requests
import json


from fuzzywuzzy import fuzz
from datetime import datetime


class GetAPI(object):
    """
    Top level class imported by kafka_apis.py.
    This class gets, and standardises, the response from the OMDB API
    for a given imdb_id. The class also hold responsibility of the topic
    it consumes from and the topic it produces to.
    """

    def __init__(self):
        self.source_topic = 'tmdb'
        self.destination_topic = 'itunes'
        self.get_data = RequestAPI().get_itunes
        self.standardise_data = Standardise().standardise
        self.choose_best = ChooseBest().get_best_match

    def get_info(self, request):
        imdb_id = request['imdb_id']
        # title - taken from omdb
        title = request['omdb_main'][0]['title']
        # release date - taken from tmdb - yyyy-dd-mm
        release_date = request['tmdb_main'][0]['release_date']
        data = self.get_data(title)
        if data is None:
            return {'itunes_main': 'no_data'}
        data = self.standardise_data(imdb_id, data)
        data = self.choose_best(data, title, release_date)
        if data is None:
            return {'itunes_main': 'no_data'}
        if data['hd_rental_price'] is None and data['rental_price'] is None:
            return {'itunes_main': 'no_data'}
        return {'itunes_main': data}


class RequestAPI(object):
    """This class requests data for a given imdb_id from the OMDB API."""

    def __init__(self):
        self.source_topic = 'tmdb'
        self.destination_topic = 'itunes'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    def get_itunes(self, title):
        """
        Gets information for a movie from the itunes API.
        :param title: The title of our film.
        :return: JSON of the itunes data.
        """
        title = title.replace(' ', '+')
        url = 'http://itunes.apple.com/search?term={0}&country=gb&media=movies&entity=movie'.format(title)
        html = requests.get(url)
        return json.loads(html.text)['results']


class Standardise(object):
    """
    This class reconstructs the response returned from the OMDB API, making
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

    def get_main_data(self, imdb_id, data):
        """
        We construct a new dictionary from teh API data, standardising the format
        so we it can be handled easily in later applications.
        :param imdb_id: The imdb_id for the film that was requested from OMDB API
        :param api_data: The raw response from the OMDB API
        :return: A standardised dictionary.
        """
        main_data = {'imdb_id': imdb_id,
                     'title': data['trackName'],
                     'url': data['trackViewUrl'].split('?')[0],
                     'released': self.fix_release_date(data['releaseDate']),
                     'hd_rental_price': data.get('trackHdRentalPrice'),
                     'rental_price': data.get('trackRentalPrice'),
                     'hd_purchase_price': data.get('trackHdPrice'),
                     'purchase_price': data.get('trackPrice')}

        return main_data

    def fix_release_date(self, release_date):
        """
        This function transforms the formatted date returned by youtube
        into a string with the format 'yyyymmdd'.
        :param release_date: Date in the formatted by youtube - 2013-07-19T04:02:19.000Z
        :return: Duration in minutes
        """
        # get the date
        release_date = release_date.split('T')[0]
        return release_date


class ChooseBest(object):
    """
    This class compares each of the films returned by the YouTube API against
    the requested film and returns the best match.
    """

    def get_best_match(self, api_data, req_title, req_release_date):
        """
        This function determines the film returned by the YouTube
        API, that best matches the film requested.
        To do this we use compare the title and the runtime of the film.
        We then pull the best result based on this.
        :param api_data: The list of dictionaries containing movie data returned from teh iTunes API.
        :param req_title: The name of the title we requested
        :param req_release_date: The release date of the requested film
        :return: The film with the best match score, or None if no match score is greater than 85.
        """
        match_scores = [self.get_match_score(e['title'], e['released'], req_title, req_release_date) for e in api_data]
        if len(match_scores) == 0:
            return None
        if max(match_scores) < 85:
            return None
        return api_data[match_scores.index(max(match_scores))]

    def get_match_score(self, title, release_date, requested_title, requested_release_date):
        """
        This returns a match score for a film returned by the YouTube API, constructed
        from the title score minus the runtime score.
        :param title: The title of the film returned by the YouTube API.
        :param requested_title: The title of the requested film.
        :return: A score out of 100.
        """
        title_score = self.get_title_score(title, requested_title)
        release_date_score = self.release_date_score(release_date, requested_release_date)
        match_score = title_score - release_date_score
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

    def release_date_score(self, release_date, requested_release_date):
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
