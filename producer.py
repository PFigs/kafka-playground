"""
    Kafka producer
    ==============

    For each topic defined within context.py, the producer
    takes the array of valid measurements and picks a
    random value from it.

    This is a very simple mock example and it would be
    straighforward to interact with a stream, transform
    it and push it to a kafka stream.

    Based on:
    https://github.com/dpkp/kafka-python
"""

import json
import time
import random
import datetime
from kafka import KafkaProducer
from context import (
    wait_for_it,
    topics,
    client_id,
    Serializer,
    measurements,
    PRODUCTION_ITEMS,
    PRODUCTION_DELTA,
)


def task_2():
    """
        Simple loop to generate mock data for temperature, pressure and humidity

        Ideally this should be hidden behind a class which would have a common
        API in order to get data, either from a mock situation such as this
        or from a proper API.

        Obtaining data from a remote API would require to clean the data to
        match it to this problem.
    """

    producer = KafkaProducer(
        client_id=client_id,
        value_serializer=lambda v: json.dumps(v, cls=Serializer).encode("utf-8"),
    )

    for _ in range(0, PRODUCTION_ITEMS):
        for topic in topics:
            args = (
                topic,
                dict(
                    measurement=random.choice(measurements[topic]),
                    measurement_time=datetime.datetime.now(),
                ),
            )
            producer.send(*args)
            producer.flush()
            time.sleep(PRODUCTION_DELTA)
            print(f"Sending: {args}")


if __name__ == "__main__":
    wait_for_it()
    task_2()
