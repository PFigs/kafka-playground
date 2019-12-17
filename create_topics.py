"""
    Kafka topic creation based on
    https://github.com/confluentinc/confluent-kafka-python
"""

from context import topics, client_id, Client
from kafka.admin import NewTopic


def task_1():
    """ Task where all necessary topics are created """

    kafka_client = Client(admin=False, client_id=client_id)

    # check which topics are currently defined and which ones are missing
    hist_topics = list()
    for topic in topics:
        hist_topics.append(f"hist_{topic}")
    topics.extend(hist_topics)

    existing_topics = kafka_client.topics
    missing_topics = set(topics) - existing_topics

    # create the missing topics
    if missing_topics:

        kafka_admin = Client(admin=True, client_id=client_id)
        topic_list = [NewTopic(name=name, num_partitions=1, replication_factor=1) for name in missing_topics]
        kafka_admin.create_topics(new_topics=topic_list, validate_only=False)

        # ensure that creation was successful
        existing_topics = kafka_client.topics
        if missing_topics - existing_topics:
            raise Exception(f"Failed to create all topics {existing_topics - missing_topics}")

    print(f"[OK] missing topics: {missing_topics}")

    return missing_topics


if __name__ == '__main__':
    task_1()
