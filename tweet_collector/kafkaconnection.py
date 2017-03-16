from confluent_kafka import Producer

class KafkaConnection():
    def __init__(self, brokers, topic):
        # Initialize a producer instance
        self._brokers = brokers
        self._topic = topic
        self._conf = {'bootstrap.servers':brokers}
        self._producer = Producer(**self._conf)

    def _delivery_callback (self, err, msg):
        if err:
            print('Kafka: Message failed delivery: %s\n' % err)
        else:
            # Debug
            print('Kafka: Message delivered to topic %s partition[%d]\n' % (msg.topic(), msg.partition()))

    def write(self, message):
        try:
            # Produce line (without newline)
            self._producer.produce(self._topic, message, callback=self._delivery_callback)

        except BufferError as e:
            print('Kafka: Local producer queue is full (%d messages awaiting delivery): try again'
                  % len(self._producer))

        self._producer.poll(0)

        # Wait until all messages have been delivered
        # Debug
        print('Kafka: Waiting for %d deliveries\n' % len(self._producer))
        self._producer.flush()
