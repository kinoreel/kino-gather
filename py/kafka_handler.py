import json
import os
import sys

from kafka import KafkaConsumer, KafkaProducer

try:
    api = __import__("get_{}".format(os.environ['API_NAME']))
except KeyError:
    try:
        api = __import__("get_{}".format(sys.argv[1]))
    except ImportError:
        print("API is not known")
        exit()

try:
    KAFKA_BROKER = os.environ['KAFKA_BROKER']
except KeyError:
    try:
        from GLOBALS import KAFKA_BROKER
    except ImportError:
        print("Specify Kafka Brokers")
        exit()


class KafkaHandler(object):

    def __init__(self):
        self.api = api.GetAPI()

        self.consumer = KafkaConsumer(group_id=self.api.destination_topic,
                                      bootstrap_servers=KAFKA_BROKER)

        self.consumer.subscribe(pattern=self.api.source_topic)

        self.producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

    def run(self):
        """
        Grab all the messages coming into any of the topics that are used by the APIs.
        Call the correct APi
        Sends the results of the API call to the next topic
        """
        for message in self.consumer:
            msg_data = json.loads(message.value.decode('utf-8'))

            api_data = self.api.get_info(msg_data)

            msg_data.update(api_data)

            self.producer.send(self.api.destination_topic, json.dumps(msg_data).encode())

if __name__ == '__main__':
    c = KafkaHandler()
    c.run()
