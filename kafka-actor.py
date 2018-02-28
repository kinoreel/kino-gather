import json
import os
import sys
from kafka import KafkaConsumer, KafkaProducer

try:
    PROCESS = __import__(os.environ['PROCESS'])
    KAFKA_BROKER = os.environ['KAFKA_BROKER']
except KeyError:
    try:
        PROCESS = __import__(sys.argv[1])
        KAFKA_BROKER = __import__(sys.argv[2])
    except ImportError:
        print("Incorrect parameters provided")
        exit()


class KafkaHandler(object):

    def __init__(self):
        self.process = PROCESS.Main()

        self.consumer = KafkaConsumer(group_id=self.process.destination_topic,
                                      bootstrap_servers=KAFKA_BROKER,
                                      auto_offset_reset='earliest')

        self.consumer.subscribe(topics=[self.process.source_topic])

        self.producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

        self.error_topic = 'errored'

    def run(self):
        """
        Grab all the messages coming into any of the topics that are used by the APIs.
        Call the correct APi
        Sends the results of the API call to the next topic
        """
        for message in self.consumer:
            msg_data = json.loads(message.value.decode('utf-8'))

            try:

                api_data = self.process.run(msg_data)

                msg_data.update(api_data)

                self.producer.send(self.process.destination_topic, json.dumps(msg_data).encode())

            except Exception as e:

                if self.process.source_topic != self.error_topic:

                    err_msg = [{'imdb_id': msg_data['imdb_id'], 'error_message': str(e)}]

                    self.producer.send(self.error_topic, json.dumps(err_msg).encode('utf-8'))

            self.consumer.commit()


if __name__ == '__main__':
    c = KafkaHandler()
    c.run()
