"""
    Kafka consumer
    ==============

    Takes that from the topics defined in context.py and
    for each of them launches a process.

    Each process exchanges the events/records with the root
    process, which is then responsible for storing them
    to a database as well as process them into an histogram
    topic.

    This seems to be what the streams API in kafka is all about.

    Based on:
    https://github.com/dpkp/kafka-python
"""

import multiprocessing
import json
import math
from context import (
    topics,
    Serializer,
    HistClient,
    DataStore,
    measurements,
    client_id,
    wait_for_it,
)
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
            bin_min=min(measurements[topic]),
            bin_max=max(measurements[topic]),
            nbins=math.ceil(len(measurements[topic]) / 2),
        )
        workers[topic] = multiprocessing.Process(
            target=consumer[topic].start, args=(queue,)
        )
        workers[topic].start()

    # waits for consumed data, publishes it back to kafka and stores it on a database
    database = DataStore("kafka.db")
    while True:
        data = queue.get(block=True)
        topic = data["type"]

        print(f"CONSUMER parent process: {json.dumps(data, cls=Serializer)}")

        producer = KafkaProducer(
            client_id=client_id,
            value_serializer=lambda v: json.dumps(v, cls=Serializer).encode("utf-8"),
        )
        producer.send(f"hist_{topic}", data["histogram"])
        producer.flush()

        database.store(topic, data)


if __name__ == "__main__":
    wait_for_it()
    task_3_4_5()
