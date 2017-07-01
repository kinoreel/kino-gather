import json

from kafka import KafkaConsumer, KafkaProducer
from get_youtube import GetYoutube


try:
    from GLOBALS import KAFKA_BROKER, YOUTUBE_API
except ImportError:
    print('Get it somewhere else')

class CollectYoutube(object):

    def __init__(self):
        self.youtube = GetYoutube(api_key=YOUTUBE_API)
        self.consumer = KafkaConsumer(group_id='youtube',
                                      bootstrap_servers=KAFKA_BROKER)
        self.consumer.subscribe(pattern='guidebox')
        self.producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)


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
            msg_data  = json.loads(message.value.decode('utf-8'))
            imdb_id = msg_data['imdb_id']
            title = msg_data['omdb_main'][0]['title']
            youtube_data = self.youtube.get_info(imdb_id, title)
            msg_data.update(youtube_data)
            self.producer.send('youtube', json.dumps(msg_data).encode())

if __name__ == '__main__':
    c = CollectYoutube()
    c.run()

