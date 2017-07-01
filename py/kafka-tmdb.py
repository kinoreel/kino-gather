import json

from get_tmdb import GetTMDB
from kafka import KafkaConsumer

try:
    from GLOBALS import KAFKA_BROKER, TMDB_API
except ImportError:
    print('Get it somewhere else')

class CollectTMDB(object):

    def __init__(self, ):
        self.tmdb = GetTMDB(TMDB_API)
        self.consumer = KafkaConsumer(group_id='tmdb',
                                      bootstrap_servers=['{}:9092'.format(KAFKA_BROKER)])
        self.consumer.subscribe(pattern='tmdb')

    def run(self):
        '''
        Collects a message from the topic 'tmdb'. This message is a json containing all the
        information collected from the apis further up the stream. We get the imdb_id from
        this data and pass it to the tmdb api. We append the information from the tmdb_api
        to the msg we collected, and then pass it to the next topic.
        '''
        for message in self.consumer:
            # message value and key are raw bytes -- decode if necessary!
            # e.g., for unicode: `message.value.decode('utf-8')
            msg_data = json.loads(message.value)
            imdb_id = msg_data['imdb_id']
            tmdb_data = GetTMDB.get_info(imdb_id)
            msg_data.extend(tmdb_data)