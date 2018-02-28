import json
import sys

from kafka import KafkaProducer

try:
    from processes.GLOBALS import KAFKA_BROKER
except ImportError:
    KAFKA_BROKER = sys.argv[1]


class PostIMDB(object):

    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

    def push_imdb_id(self, imdb_id):
        data = {'imdb_id': imdb_id}
        print('pushing'+imdb_id)
        self.producer.send('imdb_ids', json.dumps(data).encode())

if __name__ == '__main__':
    import sys
    imdb_ids = sys.argv[2]
    post = PostIMDB()
    for i in imdb_ids:
        post.push_imdb_id(i)
