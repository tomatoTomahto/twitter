from kafka import KafkaProducer
import json

class KafkaConnection():
    def __init__(self, brokers, topic):
        # Initialize a producer instance
        self._topic = topic
        self._producer = KafkaProducer(bootstrap_servers=brokers)

    def write(self, message):
        self._producer.send(self._topic, value=json.dumps(message))