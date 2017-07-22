import json
import sys

from kafka import KafkaProducer

try:
    from apis.GLOBALS import KAFKA_BROKER
except ImportError:
    print("Get it somewhere else")

producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)
try:
    data = {'imdb_id': sys.argv[1]}
    producer.send('imdb_ids', json.dumps(data).encode())
except IndexError:
    print("Please provide a imdb_id")