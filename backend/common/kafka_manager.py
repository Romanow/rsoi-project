import asyncio
import datetime
import json
from json import JSONEncoder
from threading import Thread
from typing import List

import confluent_kafka
from confluent_kafka import KafkaException
from confluent_kafka.admin import AdminClient, NewTopic
from qr_server import IQRLogger, IQRManager
from utils import *

class KafkaProducer(IQRManager):
    def __init__(self, config: dict, loop=None, poll_interval=1, logger: IQRLogger = None):
        self.logger = logger
        self.poll_interval = poll_interval

        self.connect(config)

        self._loop = loop or asyncio.get_event_loop()
        self._cancelled = False
        self._poll_thread = Thread(target=self._poll_loop)
        self._poll_thread.start()

    @retry_log_error()
    def connect(self, config):
        self._producer = confluent_kafka.Producer(config)

    def __del__(self):
        self.close()

    @staticmethod
    def get_name() -> str:
        return 'kafka_producer'

    def _poll_loop(self):
        while not self._cancelled:
            try:
                self._producer.poll(self.poll_interval)     # trigger delivery callbacks
            except Exception as e:
                if self.logger:
                    self.logger.error(f"kafka producer error: {e}")
                continue
    def close(self):
        self._cancelled = True
        self._poll_thread.join()

    def produce_dict(self, topic, value: dict, add_time=True, callback='default'):
        if add_time:
            value['time'] = int(datetime.datetime.now().timestamp())
        self.produce(topic, json.dumps(value), callback=callback)

    def produce(self, topic, value, callback='default'):
        if callback == 'default':
            callback = self._default_callback
        self._producer.produce(topic, value, on_delivery=callback)

    def _default_callback(self, err, msg):
        if self.logger:
            if err:
                self.logger.error(f"failed to produce kafka message: {err}")
            else:
                self.logger.info(f"kafka message produced: {msg}")


class KafkaConsumer(IQRManager):
    def __init__(self, config: dict, topics: List[str], callback,
                 loop=None, poll_interval=0.3, logger: IQRLogger = None, create_missing_topics: bool = False):
        self.topics = topics
        self.callback = callback

        self.logger = logger
        self.poll_interval = poll_interval

        self.connect(config, topics, create_missing_topics)

        self._loop = loop or asyncio.get_event_loop()
        self._cancelled = False
        self._poll_thread = Thread(target=self._poll_loop)
        self._poll_thread.start()

    @retry_log_error()
    def connect(self, config, topics, create_missing_topics):
        if create_missing_topics:
            self._check_create_topics(self.topics, config)

        self._consumer = confluent_kafka.Consumer(config)
        self._consumer.subscribe(topics)
        if self.logger:
            self.logger.info(f"kafka consumer subscribed to topics: {topics}")

    def _check_create_topics(self, topics, config):
        admin_client = AdminClient({'bootstrap.servers': config['bootstrap.servers']})
        available_topics = admin_client.list_topics()
        available_topics = list(available_topics.topics.keys())

        new_topics = []
        missing_topic_names = []
        for t in topics:
            if t not in available_topics:
                nt = NewTopic(t, num_partitions=3, replication_factor=1)
                new_topics.append(nt)
                missing_topic_names.append(t)

        if len(missing_topic_names) == 0:
            if self.logger:
                self.logger.info(f'kafka consumer: found all needed topics')
            return

        if self.logger:
            self.logger.info(f'kafka consumer requests to create topics: {missing_topic_names}')

        fs = admin_client.create_topics(new_topics)
        for topic, f in fs.items():
            try:
                f.result()
                print("Topic {} created".format(topic))
            except Exception as e:
                print("Failed to create topic {}: {}".format(topic, e))

    @staticmethod
    def get_name() -> str:
        return 'kafka_consumer'

    def _poll_loop(self):
        while not self._cancelled:
            try:
                msg = self._consumer.poll(self.poll_interval)     # trigger delivery callbacks

                if msg is None:
                    continue
                if msg.error():
                    if self.logger:
                        self.logger.error(f"kafka consumer error: {msg.error()}")
                    continue

                if self.logger:
                    self.logger.info(f"kafka consumed message: {msg}")

                self.callback(msg)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"kafka consumer error: {e}")
                continue

    def close(self):
        self._cancelled = True
        self._poll_thread.join()
