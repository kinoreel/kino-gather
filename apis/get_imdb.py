import json
import sys

from kafka import KafkaProducer

try:
    from api.GLOBALS import KAFKA_BROKER
except ImportError:
    from GLOBALS import KAFKA_BROKER

producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)
try:
    data = {'imdb_id': sys.argv[1]}
    producer.send('imdb_ids', json.dumps(data).encode())
except IndexError:
    print("Please provide a imdb_id")