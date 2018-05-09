import json
import os
import sys
from kafka import KafkaConsumer, KafkaProducer
import importlib
import traceback


class KafkaHandler(object):

    def __init__(self, process_name: str, kafka_broker: str):

        self.process_name = process_name

        self.process = importlib.import_module('processes.{0}'.format(self.process_name)).Main()

        self.consumer = KafkaConsumer(group_id=self.process.destination_topic,
                                      bootstrap_servers=kafka_broker,
                                      auto_offset_reset='earliest')

        self.consumer.subscribe(topics=[self.process.source_topic])

        self.producer = KafkaProducer(bootstrap_servers=kafka_broker)

        self.error_topic = 'errored'

    def run(self):
        """
        Grab all the messages coming into any of the topics that are used by the APIs.
        Call the correct API
        Sends the results of the API call to the next topic
        """

        for message in self.consumer:

            print(message)
            msg_data = json.loads(message.value.decode('utf-8'))

            try:

                print(msg_data)
                api_data = self.process.run(msg_data)

                print(api_data)

                if api_data:
                    msg_data.update(api_data)

                    self.producer.send(self.process.destination_topic, json.dumps(msg_data).encode())

            except Exception:

                print('exception')

                if self.process.source_topic != self.error_topic:

                    err_msg = [{'imdb_id': msg_data['imdb_id'],
                                'error_message': '{0}: {1}'.format(self.process_name, traceback.format_exc())}]

                    self.producer.send(self.error_topic, json.dumps(err_msg).encode('utf-8'))

            self.consumer.commit()


if __name__ == '__main__':

    try:
        PROCESS_NAME = os.environ['PROCESS']
        KAFKA_BROKER = os.environ['KAFKA_BROKER']
    except KeyError:
        PROCESS_NAME = sys.argv[1]
        KAFKA_BROKER = sys.argv[2]

    c = KafkaHandler(PROCESS_NAME, KAFKA_BROKER)
    c.run()
