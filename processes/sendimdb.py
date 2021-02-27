import json

from kafka import KafkaProducer, KafkaConsumer

KAFKA_BROKER = ''


class PostIMDB(object):

    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)
        self.consumer = KafkaConsumer(bootstrap_servers=KAFKA_BROKER, auto_offset_reset="earliest")

    def push_imdb_id(self, imdb_id):
        data = {'imdb_id': imdb_id}
        self.producer.send('imdb_ids', json.dumps(data).encode())


if __name__ == '__main__':
    import sys
    try:
        imdb_id = sys.argv[1]
    except IndexError:
        imdb_id = 'tt0120737'
    post = PostIMDB()
    post.push_imdb_id(imdb_id)
    post.consumer.subscribe(['imdb_ids'])
    for i in post.consumer:
        print(i)
