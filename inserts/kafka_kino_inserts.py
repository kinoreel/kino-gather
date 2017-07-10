import json
import os
import sys
from kafka import KafkaConsumer, KafkaProducer

import GLOBALS

try:
    table_name = __import__("insert_{}".format(os.environ['TABLE_NAME']))
except KeyError:
    try:
        table_name = __import__("insert_{}".format(sys.argv[1]))
    except ImportError:
        print("Table name is not known")
        exit()

try:
    KAFKA_BROKER = os.environ['KAFKA_BROKER']
    PG_SERVER = os.environ['PG_SERVER']
    PG_PORT = os.environ['PG_PORT']
    PG_DB = os.environ['PG_DB']
    PG_USERNAME = os.environ['PG_USERNAME']
    PG_PASSWORD = os.environ['PG_PASSWORD']
except KeyError:
    try:
        from GLOBALS import KAFKA_BROKER, PG_SERVER, PG_PORT, PG_DB, PG_USERNAME, PG_PASSWORD
    except ImportError:
        print("Specify Kafka Brokers")
        exit()


class KafkaInsertHandler(object):

    def __init__(self):
        self.table_name = table_name.InsertData(PG_SERVER, PG_PORT, PG_DB, PG_USERNAME, PG_PASSWORD)

        self.consumer = KafkaConsumer(group_id=self.table_name.destination_topic,
                                      bootstrap_servers=KAFKA_BROKER,
                                      auto_offset_reset='earliest')

        self.consumer.subscribe(pattern=self.table_name.source_topic)

        self.producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

    def run(self):
        """
        Grab all the messages coming into any of the topics INSERT topics.
        Insert the data into kino@kino.
        Sends the results to the next topic.
        """
        for message in self.consumer:
            msg_data = json.loads(message.value.decode('utf-8'))

            producer_data = self.table_name.insert(msg_data)

            if producer_data:

                self.producer.send(self.table_name.destination_topic, json.dumps(producer_data).encode())

if __name__ == '__main__':
    c = KafkaInsertHandler()
    c.run()
