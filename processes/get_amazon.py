import requests
import os
import hmac
import hashlib
import base64
import time
from bs4 import BeautifulSoup
from datetime import datetime
from fuzzywuzzy import fuzz

try:
    AWS_API_KEY = os.environ['AWS_API_KEY']
except KeyError:
    try:
        from processes.GLOBALS import AWS_API_KEY
    except ImportError:
        print("No API key provided")
        exit()


class Main(object):
    """
    Top level class imported by kafka_apis.py.
    Gets and standardises the response from the iTunes API.
     The class also hold responsibility of the topic it consumes from and the topic it produces to.
    """

    def __init__(self):
        self.source_topic = 'itunes'
        self.destination_topic = 'amazon'

    def run(self, request):
        # Get information on film collected from upstream apis
        imdb_id, title, release_date, runtime = self.retrieve_data(request)

        # TODO fix amazon api so we can actually gather data
        # api_response = RequestAPI().get_amazon(title)
        #
        # standardised_data = StandardiseResponse(api_response).standardise()
        #
        # film = ChooseBest.get_best_match(standardised_data, title, runtime, release_date)
        film = None
        if film is None:
            return {'amazon_main': []}

        film['imdb_id'] = imdb_id

        return {'amazon_main': [film]}

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
        runtime = request['tmdb_main'][0]['runtime']
        return imdb_id, title, release_date, runtime


class RequestAPI(object):
    """Requests data for a given imdb_id from the OMDB API."""

    def __init__(self, api_key=AWS_API_KEY):
        self.api_key = api_key
        self.headers = {'User-Agent':
                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    def get_amazon(self, title):
        """
        For a given imdb_id, we construct the API url, make a get request,
        and return the response as a JSON object.
        :param imdb_id: The imdb_id of the film we are requesting.
        :return: A JSON object containing the response for the given imdb_id.
        """
        url = 'http://webservices.amazon.co.uk/onca/xml'
        parameters = 'AWSAccessKeyId=AKIAJKQ27VUSOVVCZSWA' \
                     'AssociateTag=kinoproject-21' \
                     'Keywords=' + self.rfc_3986_encode(title) + '&' \
                                                                 'Operation=ItemSearch&' \
                                                                 'ResponseGroup=ItemAttributes%2COffers&' \
                                                                 'SearchIndex=All&' \
                                                                 'Service=AWSECommerceService&' \
                                                                 'Timestamp=' + self.rfc_3986_encode(
            self.get_timestamp())
        signature = self.get_signature(parameters, self.api_key)
        encoded_signature = self.rfc_3986_encode(signature.decode('utf-8'))
        url = '{0}?{1}&Signature={2}'.format(url, parameters, encoded_signature)
        response = self.request_api(url)
        return response

    def request_api(self, url):
        """
        Amazon has throttling, therefore we run a number of retries with increasing waits
        if we hit status 503.
        :param url: The api url
        :return: html response
        """
        max_retries = 5
        for i in range(0, max_retries):
            html = requests.get(url, headers=self.headers)
            if html.status_code != 503:
                return html.text
            time.sleep(i)
        return html.text

    def rfc_3986_encode(self, string):
        result = ''
        accepted = [c for c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~'.encode('utf-8')]
        for char in string.encode('utf-8'):
            result += chr(char) if char in accepted else '%{}'.format(hex(char)[2:]).upper()
        return result

    def get_timestamp(self):
        """
        Hello, I am amazon. I am a ball ache
        :return: A signed request as detailed here -
        https://docs.aws.amazon.com/AWSECommerceService/latest/DG/rest-signature.html
        """
        # UTC timestamp in the form 2014-08-18T12:00:00Z
        timestamp = str(datetime.utcnow())
        timestamp = timestamp.replace(' ', 'T')
        return timestamp

    def get_signature(self, url_params, aws_secret_key):
        signature = hmac.new(key=bytes(aws_secret_key, 'latin-1'),
                             msg='GET\nwebservices.amazon.co.uk\n/onca/xml\n{0}'.format(url_params).encode('utf-8'),
                             digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(signature).strip()
        return signature


class StandardiseResponse(object):
    """
    This class standardises the response returned from the OMDB API,
    removing unwanted data, and structuring the remaining data
    so that it is easier to handle in later processes.
    """

    def __init__(self, api_response):
        """
        Constructs a new dictionary from the API data.
        :param imdb_id: The imdb_id for the requested film
        :param api_data: The raw response from the Amazon Product Search API
        :return: A standardised dictionary.
        """
        self.api_response = api_response

    def standardise(self):
        split_data = BeautifulSoup(self.api_response, "html.parser").find_all('item')
        standardised_response = [self.get_main_data(item) for item in split_data]
        return standardised_response

    def get_main_data(self, item):
        main_data = {
            'title': item.find('title').text,
            'url': item.find('detailpageurl').text,
            'productType': item.find('producttypename').text,
            'binding': self.get_binding(item),
            'runtime': self.get_runtime(item),
            'released': self.get_release_date(item),
            'price': self.get_price(item),
            'currency': self.get_currency(item)
        }
        return main_data

    def get_binding(self, item):
        try:
            return item.find('binding').text
        except AttributeError:
            return None

    def get_price(self, item):
        try:
            return int(item.find('amount').text) / 100
        except AttributeError:
            return None

    def get_currency(self, item):
        try:
            return item.find('currencycode').text
        except AttributeError:
            return None

    def get_release_date(self, item):
        try:
            return item.find('releasedate').text
        except AttributeError:
            return None

    def get_runtime(self, item):
        try:
            return int(item.find('runningtime').text)
        except AttributeError:
            return None


class ChooseBest(object):
    """
    This class compares each of the films returned by the Amazon API against
    the requested film and returns the best match.
    """

    @staticmethod
    def get_best_match(items, req_title, req_runtime, req_release_date):
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
        films = ChooseBest.get_amazon_video_products(items)
        match_scores = [ChooseBest.get_match_score(e['title'],
                                                   e['runtime'],
                                                   e['released'],
                                                   req_title,
                                                   req_runtime,
                                                   req_release_date)
                        for e in films]
        if len(match_scores) == 0:
            return None
        if max(match_scores) < 85:
            return None
        return films[match_scores.index(max(match_scores))]

    @staticmethod
    def get_amazon_video_products(items):
        return [e for e in items if e['productType'] == 'DOWNLOADABLE_MOVIE' and e['binding'] == 'Amazon Video']

    @staticmethod
    def get_match_score(title, runtime, release_date, requested_title, requested_runtime, requested_release_date):
        """
        This returns a match score for a film returned by the YouTube API, constructed
        from the title score minus the runtime score.
        :param title: The title of the film returned by the YouTube API.
        :param runtime: The runtime of the film returned by the YouTube API
        :param requested_title: The title of the requested film.
        :param requested_runtime: The runtime of the requested film.
        :return: A score out of 100.
        """
        title_score = ChooseBest.get_title_score(title, requested_title)
        runtime_score = ChooseBest.get_runtime_score(runtime, requested_runtime)
        release_date_score = ChooseBest.get_release_date_score(release_date, requested_release_date)
        match_score = title_score - (runtime_score + release_date_score)
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
        try:
            upload_date = datetime.strptime(upload_date, '%Y-%m-%d')
        except TypeError:
            # We were not provided a release_date, so we just let the test pass.
            return 0
        requested_release_date = datetime.strptime(requested_release_date, '%Y-%m-%d')
        # If the upload date is greater then the release date then we return
        # the number of months it as uploaded before it was released. This will
        # be taken away from the match score.
        days = (upload_date - requested_release_date).days
        if days < 0:
            return abs(round(days / 30))
        return 0


if __name__ == '__main__':
    a = Main()
    request = {'imdb_id': 'tt3155242',
               'tmdb_main': [{'title': 'Partisan', 'runtime': 94, 'release_date': '2016-01-08'}]}
    result = a.run(request)
    print(result)
