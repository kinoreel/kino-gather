import json

from kafka import KafkaConsumer, KafkaProducer
from get_guidebox import GetGuidebox

try:
    from GLOBALS import KAFKA_BROKER, GUIDEBOX_API
except ImportError:
    print('Get it somewhere else')

class CollectTMDB(object):

    def __init__(self):
        self.guideBox = GetGuidebox(GUIDEBOX_API)
        self.topic = 'guidebox'
        self.consumer = KafkaConsumer(group_id=self.topic,
                                      bootstrap_servers=KAFKA_BROKER)
        self.consumer.subscribe(pattern='tmdb')
        self.producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

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
            guideBox_data = self.guideBox.get_info(imdb_id)
            msg_data.update(guideBox_data)

            self.producer.send(self.topic,
                               json.dumps(msg_data).encode())


if __name__ == '__main__':
    c = CollectTMDB()
    c.run()