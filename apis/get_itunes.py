import requests
import json

class GetAPI(object):

    def __init__(self):
        self.source_topic = 'youtube'
        self.destination_topic = 'movies'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    def get_info(self, request):
        '''
        Hits the itunes api for a movie, cleans the data,
        and returns its
        :return: JSON of our cleaned data taken from the itunes API
        '''
        imdb_id = request['imdb_id']
        title = request['omdb_main'][0]['title']
        data = self.get_itunes_json(title)['results'][0]
        return self.split_data(imdb_id, title, data)

    def get_itunes_json(self, title):
        '''
        Gets information for a movie from the itunes API.
        :param title: The title of our film.
        :return: JSON of the itunes data.
        '''
        title = title.replace(' ', '+')
        url = 'http://itunes.apple.com/search?term=' + title + '&county=UK&media=movies&entity=movie'
        html = requests.get(url)
        return json.loads(html.text)

    def split_data(self, imdb_id, title, data):
        '''
        Splits the json API, into more usable data
        :param data: The json we received the itunes API.
        :return: A list of dictionaries, where each dictionary is a
        different type of information.
        '''
        result = {}
        result['itunes_main']={'imdb_id':imdb_id,
                                'title':title,
                                'released':data['releaseDate'],
                                'hd_rental_price':data['trackHdRentalPrice'],
                                'rental_price':data['trackRentalPrice'],
                                'hd_purchase_price':data['trackHdPrice'],
                                'purchase_price':data['trackPrice']}
        return result


