import json

from kafka import KafkaConsumer, KafkaProducer

from get_omdb import GetOMDB


try:
    from GLOBALS import KAFKA_BROKER, OMDB_API
except ImportError:
    print('Get it somewhere else')

class CollectOMDB(object):

    def __init__(self):
        self.omdb = GetOMDB(api_key = OMDB_API)
        self.topic = 'omdb'
        self.consumer = KafkaConsumer(group_id = self.topic,
                                      bootstrap_servers=KAFKA_BROKER)
        self.consumer.subscribe(pattern = 'imdb_ids')
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
            msg_data  = json.loads(message.value)
            imdb_id = msg_data['imdb_id']
            omdb_data = self.omdb.get_info(imdb_id)
            msg_data.update(omdb_data)
            self.producer.send(self.topic, json.dumps(msg_data).encode())
            print('Processed: {}'.format(imdb_id))

if __name__ == '__main__':
    c = CollectOMDB()
    c.run()






