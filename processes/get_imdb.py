import json

from kafka import KafkaProducer

from GLOBALS import KAFKA_BROKER

class PostIMDB(object):

    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

    def push_imdb_id(self, imdb_id):
        data = {'imdb_id': imdb_id}
        self.producer.send('imdb_ids', json.dumps(data).encode())

if __name__ == '__main__':
    import sys
    imdb_ids = sys.argv[0]
    post = PostIMDB()
    for i in imdb_ids:
        post.push_imdb_id(i)
