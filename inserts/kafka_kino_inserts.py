import json
import os
import sys
from kafka import KafkaConsumer, KafkaProducer

from apis import GLOBALS

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
except KeyError:
    try:
        from apis.GLOBALS import KAFKA_BROKER
    except ImportError:
        print("Specify Kafka Brokers")
        exit()


class KafkaInsertHandler(object):

    def __init__(self):
        self.table_name = table_name.InsertData(GLOBALS.PG_SERVER, GLOBALS.PG_PORT, GLOBALS.PG_DB_DEV, 'kino', 'kino123')

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
