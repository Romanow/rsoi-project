import json

from confluent_kafka import Consumer, Producer
from confluent_kafka.admin import AdminClient, NewTopic

def create_topics():
    a = AdminClient({'bootstrap.servers': 'localhost:29092'})

    topics = 'using_filters searching view_author view_series view_book download_book'
    new_topics = [NewTopic(topic, num_partitions=3, replication_factor=1) for topic in topics.split(' ')]
    # Note: In a multi-cluster production scenario, it is more typical to use a replication_factor of 3 for durability.

    # Call create_topics to asynchronously create topics. A dict
    # of <topic,future> is returned.
    fs = a.create_topics(new_topics)

    # Wait for each operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print("Topic {} created".format(topic))
        except Exception as e:
            print("Failed to create topic {}: {}".format(topic, e))


def produce():
    p = Producer({'bootstrap.servers': 'localhost:29092'})

    def delivery_report(err, msg):
        """ Called once for each message produced to indicate delivery result.
            Triggered by poll() or flush(). """
        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

    for data in [{'a': 1}, {'b': 2}]:
        # Trigger any available delivery report callbacks from previous produce() calls
        p.poll(0)

        # Asynchronously produce a message. The delivery report callback will
        # be triggered from the call to poll() above, or flush() below, when the
        # message has been successfully delivered or failed permanently.
        p.produce('view_book', json.dumps(data), callback=delivery_report)

    # Wait for any outstanding messages to be delivered and delivery report
    # callbacks to be triggered.
    p.flush()


def consume():
    c = Consumer({
        'bootstrap.servers': 'localhost:29092',
        'group.id': 'qrook_scout',
        'auto.offset.reset': 'earliest',        # latest
        "enable.auto.commit": 'true'
    })

    c.subscribe(['view_book'])

    while True:
        msg = c.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue

        data = json.loads(msg.value())
        print('Received message:', data)

    c.close()


if __name__ == '__main__':
    create_topics()
    #produce()
    #consume()