import sys

from confluent_kafka import Consumer, KafkaException, Producer
from confluent_kafka.admin import AdminClient, NewTopic


def create_topic(topic, num_partitions=1, replication_factor=1):
    admin_client = AdminClient({'bootstrap.servers': 'localhost:9092'})
    topic_config = {
        'topic': topic,
        'num_partitions': num_partitions,
        'replication_factor': replication_factor
    }
    futures = admin_client.create_topics([NewTopic(**topic_config)])

    for topic, future in futures.items():
        try:
            future.result()  # This will raise an exception if topic creation fails
            print(f'Topic {topic} created')
        except Exception as e:
            print(f'Failed to create topic {topic}: {e}')
            sys.exit(1)


def produce_message(topic, message):
    p = Producer({'bootstrap.servers': 'localhost:9092'})

    try:
        p.produce(topic, message.encode('utf-8'))
        p.flush()
        print(f'Message "{message}" produced successfully to topic {topic}')
    except KafkaException as e:
        print(f'Failed to produce message: {e}')


def consume_messages(topic):
    c = Consumer({
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'mygroup',
        'auto.offset.reset': 'earliest'
    })

    c.subscribe([topic])

    while True:
        msg = c.poll(1.0)

        if msg is None:
            continue
        if msg.error():
            print(f'Consumer error: {msg.error()}')
            continue

        print(f'Received message: {msg.value().decode("utf-8")}')
        return

    c.close()

def delete_topic(topic):
    admin_client = AdminClient({'bootstrap.servers': 'localhost:9092'})

    # Delete the topic
    fs = admin_client.delete_topics([topic])

    # Wait for operation to finish and check results
    for topic, f in fs.items():
        try:
            f.result()  # This will raise an exception if topic deletion fails
            print(f'Topic, {topic} deleted successfully')
        except Exception as e:
            print(f'Failed to delete topic {topic}: {e}')
            sys.exit(1)


if __name__ == '__main__':
    topic_name = 'the_topic'

    # Create the topic (you can comment this out after the first run)
    create_topic(topic_name)

    # Produce a message
    produce_message(topic_name, 'Hello, Kafka!')

    # Consume messages (run in a separate terminal or concurrently)
    consume_messages(topic_name)

    # Delete topic
    delete_topic(topic_name);
    sys.exit()
