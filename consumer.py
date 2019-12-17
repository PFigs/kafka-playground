"""
    Kafka consumer based on
    https://github.com/confluentinc/confluent-kafka-python
"""

import multiprocessing
import json
import math
from context import topics, Serializer, HistClient, DataStore, measurements, client_id
from kafka import KafkaProducer


def task_3_4_5():
    """ This method contains the solution for tasks 3, 4 and 5 """

    manager = multiprocessing.Manager()
    queue = manager.Queue()
    consumer = dict()
    workers = dict()

    # Consumes the produced data
    for topic in topics:
        consumer[topic] = HistClient(
            topic=topic,
            producer_topic=f"hist_{topic}",
            bin_min=min(measurements[topic]),
            bin_max=max(measurements[topic]),
            nbins=math.ceil(len(measurements[topic])/2))
        workers[topic] = multiprocessing.Process(target=consumer[topic].start, args=(queue,))
        workers[topic].start()

    # waits for consumed data, publishes it back to kafka and stores it on a database
    database = DataStore("kafka.db")
    while True:
        data = queue.get(block=True)
        topic = data["type"]

        print(f"CONSUMER parent process: {json.dumps(data, cls=Serializer)}")

        producer = KafkaProducer(client_id=client_id, value_serializer=lambda v: json.dumps(v, cls=Serializer).encode('utf-8'))
        producer.send(f"hist_{topic}", data["histogram"])
        producer.flush()

        database.store(topic, data)


if __name__ == '__main__':
    task_3_4_5()
