"""
    Context
    =======

    Contains classes and useful variables that are
    shared among the example scripts

"""

import datetime
import enum
import json
import sqlite3
import numpy
import plotille
import socket
import time

from kafka.admin import KafkaAdminClient
from kafka.client import KafkaClient
from kafka import KafkaConsumer

# Controls the data generation
PRODUCTION_ITEMS = 5000
PRODUCTION_DELTA = 1

# client id
client_id = "silvap"

# Topics and their value range
topics = ["humidity", "temperature", "pressure"]

# measurement ranges
measurements = dict()
measurements["temperature"] = range(-25, 25, 1)
measurements["pressure"] = range(800, 1200, 100)
measurements["humidity"] = range(40, 80, 1)


class Serializer(json.JSONEncoder):
    """ Specialization of the JSON encoder """

    # As instructed by the python docs, likely a pylint issue
    # pylint: disable=method-hidden, arguments-differ
    def default(self, obj):
        """ Handles serialization of common types """
        if isinstance(obj, datetime.datetime):
            return f"{datetime.datetime.isoformat(obj)}"
        if isinstance(obj, enum.Enum):
            return obj.value
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return super().default(obj)


class Client:
    """
    Client for Kafka

    This class allows for the creation of a standard or admin kafka client.

    It also provides utilities to inspect existing topics.
    """

    def __init__(self, hostname="localhost", port=9092, admin=False, client_id="pycli"):
        super().__init__()
        connection_string = f"{hostname}:{port}"
        if not admin:
            self._client = KafkaClient(bootstrap_servers=connection_string)
        else:
            self._client = KafkaAdminClient(
                bootstrap_servers=connection_string, client_id=client_id
            )

    @property
    def topics(self):
        """ Returns the current kafka topics """
        future = self._client.cluster.request_update()
        self._client.poll(future=future)
        _topics = set(self._client.cluster.topics())
        return _topics

    def __getattr__(self, attr):
        return getattr(self._client, attr)


class HistClient:
    """
    HistClient

    This class consumes the API data and produces an histogram
    out of it.

    The histogram is offloaded to a queue where a producer sends
    it back to kafka and writes it to a database.

    """

    def __init__(self, topic, bin_min=-100, bin_max=100, nbins=10):
        super().__init__()
        self._nbins = nbins
        self._bin_edges = numpy.linspace(bin_min, bin_max, nbins + 1)
        self._hist = numpy.zeros(nbins)

        self._topic = topic
        self._consumer = KafkaConsumer(
            self._topic, client_id=client_id, value_deserializer=json.loads
        )

    def consume(self):
        """
            Obtains a message from a kafka topic and computes the histogram.

            Returns:
                A dictionary with the kafka message, histogram and bin edges
        """
        for msg in self._consumer:
            count, _ = numpy.histogram(msg.value["measurement"], bins=self._bin_edges)
            self._hist += count
            yield {
                "type": self._topic,
                self._topic: msg.value,
                "histogram": {"hist": self._hist, "bin_edges": self._bin_edges},
            }

    @staticmethod
    def plot(hist, bin_edges):
        """ Makes a scatter plot based on the current histogram and bin edges"""
        return plotille.scatter(bin_edges[:-1], hist)

    def start(self, queue):
        """ Initiates the topic consumption """
        for message in self.consume():
            queue.put(message)


class DataStore:
    """
    DataStore

    This is a very basic abstraction to hide away the
    SQL lite. Ideally one should aim for a proper
    ORM to easily segregate data from database
    technology.
    """

    def __init__(self, filepath):
        super().__init__()
        self.connection = sqlite3.connect(filepath, isolation_level=None)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        """ Creates the measurement tables based on each topic"""

        for topic in topics:
            try:
                self.cursor.execute(
                    f"CREATE TABLE {topic} (date DATETIME, value INTEGER, hist JSON)"
                )
            except sqlite3.OperationalError:
                pass

    def store(self, table, data):
        """ Stores the measurement data in the respective table """
        self.cursor.execute(
            f"INSERT INTO {table} VALUES (?,?,?)",
            (
                data[table]["measurement_time"],
                data[table]["measurement"],
                json.dumps(data["histogram"], cls=Serializer),
            ),
        )


def wait_for_it(host="localhost", port=9092, timeout=1):
    """ Simple method that waits for a target socket to be available """

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            s.connect((host, port))
            break
        except Exception:
            pass
        time.sleep(timeout)
        continue
