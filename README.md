# kafka-playground

[![Build Status](https://travis-ci.com/PFigs/kafka-playground.svg?branch=master)](https://travis-ci.com/PFigs/kafka-playground)

A playground to explore kafka concepts

Install Landoop Kafka development environment from <https://github.com/lensesio/fast-data-dev>

## Task 1

Specify new Kafka topic or topics that handles
publishing of temperature, humidity and air pressure.

### Solution

The topics _temperature, humidity and air pressure_ are defined under
[context.py][context].
The array of topics is used by [create_topics.py][create_topics] to first inspect
if they already exist created and if not it creates them as well as the
histogram topics.

## Task 2

Create service that publishes new values on topic(s) specified in task 1.
Data can be mocked or from real source, up to you.

### Solution

Data for the three topics is mocked within [producer.py][producer].
A good extension would be to acquire data from a source such as
[darksky.net][darksky],
clean it up and feed it to the current topics.

## Task 3, 4 and 5

1.  Create consumer for topic(s) to create real time histograms of the values.
2.  Push the histograms back to Kafka as a new topic.
3.  Store data to database/format of your choice.

### Solution

These three tasks are tackled with [consumer.py][consumer]. Two additional
scripts provide additional facilities to inspect the database content
(see [view_database.py][viewdb]) and to make a simple scatter
plotter based on the  realtime histogram values
(see [plotter.py][plotter]).

In [consumer.py][consumer] each kafka topic is consumed through an instance
of the HistClient class. Each of these classes runs on a separate process
and exchange data with the root process through a syncronous pipe.

For each message that the main process receives, it is written to a database
and the histogram values are published under each measurement's histogram
topic.

## Overview: installation, code and setup

The application examples in this repository are written
in Python +3 and linted with black. The
main package in use is kafka-python which offers a very simple
interface to create, publish and subscribe to topics.

The solution has been kept simple, where a single script file
aims to tackle each of the defined tasks. Some common code
is shared among these scripts, through the context.py file.

In terms of the database choice, simplicity and lack of requirements
was the reason behind going with sqlite. It requires no extra
host dependency and it server the purpose to illustrate
the concept of storing data to a relational database.

### Installation

Executing the python code requires at least Python 3 (3.7 is
the tested and recommended version), as well as PIP.

Install the dependencies with

        pip install -r requirements.txt

### Setup

Once the requirements are met, you can execute the example
scripts. The first script to execute should be the create
topics. Afterwards you should launch the consumer and then
the producer. If you wish to view the realtime histogram,
you can rely on the plotter script to display a scatter
plot with the current values of the histogram.

Each script is executed with

        python <script name>

If you wish to launch kafka and all the services, please build
the container and launch the services using docker-compose as

        docker-compose up -d

[context]: ./context.py

[create_topics]: ./create_topics.py

[producer]: ./producer.py

[consumer]: ./consumer.py

[plotter]: ./plotter.py

[viewdb]: ./view_database.py

[darksky]: https://darksky.net/dev/docs#api-request-types
