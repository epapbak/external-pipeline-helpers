from kafka import KafkaProducer
import json
import logging
import threading
import time
from datetime import datetime, timezone
import random, string


class MessageProducer:
    broker = ""
    topic = ""
    producer = None

    def __init__(self, broker, topic):
        self.broker = broker
        self.topic = topic
        self.producer = KafkaProducer(bootstrap_servers=self.broker,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks='all',
        retries = 3)

    def generate_request_id(self):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(32))

    def send_msgs(self, headers, msg, waitFor):
        while True:
            msg["timestamp"] = datetime.now(timezone.utc).isoformat()
            msg["request_id"] = self.generate_request_id()
            print("sending message...")
            try:
                future = self.producer.send(self.topic, value=msg, headers=headers)
                self.producer.flush()
                future.get(timeout=60)
                logging.info('msg sent')
                time.sleep(waitFor)
            except Exception as ex:
                logging.info('msg timed out')
                logging.error(ex)

def work(producer, headers, data, waitFor):
    producer.send_msgs(headers, data, waitFor)


if __name__ == "__main__":
    broker = '127.0.0.1:9092' #'host.docker.internal:9092'
    topic = 'platform.upload.announce'

    message_producer1 = MessageProducer(broker,topic)
    message_producer2 = MessageProducer(broker,topic)

    data1 = {
        "url": "http://archiveserver:12380/insight_archive",
        "b64_identity": "eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAiMDAwMDAwMSIsICJpbnRlcm5hbCI6IHsib3JnX2lkIjogIjEifX19Cg==",#"eyJpZGVudGl0eSI6IHsiaW50ZXJuYWwiOiB7Im9yZ19pZCI6ICIxMjM0NTY3OCJ9fX0K",
        "account": 123456,
    }

    data2 = {
        "url": "http://archiveserver:12380/insight_archive_workload",
        "b64_identity": "eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAiMDAwMDAwMSIsICJpbnRlcm5hbCI6IHsib3JnX2lkIjogIjEifX19Cg==",#"eyJpZGVudGl0eSI6IHsiaW50ZXJuYWwiOiB7Im9yZ19pZCI6ICIxMjM0NTY3OCJ9fX0K",
        "account": 654321,
    }

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S.%f")

    threads = list()
    for index in range(4):
        logging.info("Main    : create and start thread %d.", index)
        x = threading.Thread(target=work, args=(message_producer1, [('service', b'stoff')], data1, 1))
        y = threading.Thread(target=work, args=(message_producer2, [('service', b'openshift')], data1, 1))
        z = threading.Thread(target=work, args=(message_producer2, [('service', b'openshift')], data2, 10))
        threads.append(x)
        threads.append(y)
        threads.append(z)
        x.start()
        y.start()
        z.start()

    for index, thread in enumerate(threads):
        logging.info("Main    : before joining thread %d.", index)
        thread.join()
        logging.info("Main    : thread %d done", index)


