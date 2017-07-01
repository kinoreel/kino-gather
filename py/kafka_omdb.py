import json

from kafka import KafkaConsumer

from get_omdb import GetOMDB

consumer = KafkaConsumer(group_id = 'omdb',
                         bootstrap_servers = ['212.111.42.214:9092'])


try:
    from GLOBALS import KAFKA_BROKER, OMDB_API
except ImportError:
    print('Get it somewhere else')

class CollectOMDB(object):

    def __init__(self):
        self.omdb = GetOMDB(api_key = OMDB_API)
        self.consumer = KafkaConsumer(group_id = 'omdb',
                                      bootstrap_servers = ['{0}'.format(KAFKA_BROKER)])
        self.consuer.subscribe(pattern = 'omdb')

    def run(self):
        '''
        Collects a message from the topic 'omdb'. This message is a json containing all the
        information collected from the apis further up the stream. We get the imdb_id from
        this data and pass it to the tmdb api. We append the information from the tmdb_api
        to the msg we collected, and then pass it to the next topic.
        '''
        for message in self.consumer:
            # message value and key are raw bytes -- decode if necessary!
            # e.g., for unicode: `message.value.decode('utf-8')
            msg_data  = json.loads(message.value)
            imdb_id = msg_data['imdb_id']
            omdb_data = self.omdb.get_info(imdb_id)
            msg_data.extend(omdb_data)





