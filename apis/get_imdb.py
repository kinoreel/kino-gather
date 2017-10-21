import json

from kafka import KafkaProducer

try:
    from api.GLOBALS import KAFKA_BROKER
except ImportError:
    from GLOBALS import KAFKA_BROKER

class PostIMDB(object):

    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

    def push_imdb_id(self, imdb_id):
        data = {'imdb_id': imdb_id}
        self.producer.send('imdb_ids', json.dumps(data).encode())

if __name__=='__main__':
    import sys
    imdb_id = sys.argv[1]
    post = PostIMDB()
    post.push_imdb_id(imdb_id)
