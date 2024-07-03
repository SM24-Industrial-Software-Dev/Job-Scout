##Comment the return and sys.exit() statements to run the test script with print statements
##For Docker, the container would exit due to return and sys.exit() so I commented them out

import sys
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import NewTopic, KafkaAdminClient


def create_topic(topic, num_partitions=1, replication_factor=1):
    admin_client = KafkaAdminClient(bootstrap_servers='kafka:9092')

    topic_list = [NewTopic(name=topic, num_partitions=num_partitions, replication_factor=replication_factor)]
    
    try:
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        print(f'Topic {topic} created')
    except Exception as e:
        print(f'Failed to create topic {topic}: {e}')
        sys.exit(1)
    finally:
        admin_client.close()

def produce_message(topic, message):
    producer = KafkaProducer(bootstrap_servers='kafka:9092')
    
    try:
        producer.send(topic, message.encode('utf-8'))
        producer.flush()
        print(f'Message "{message}" produced successfully to topic {topic}')
    except Exception as e:
        print(f'Failed to produce message: {e}')
    finally:
        producer.close()

def consume_messages(topic):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers='kafka:9092',
        group_id='mygroup',
        auto_offset_reset='earliest'
    )

    try:
        for msg in consumer:
            print(f'Received message: {msg.value.decode("utf-8")}')
            return
    except Exception as e:
        print(f'Consumer error: {e}')
    finally:
        consumer.close()

def delete_topic(topic):
    admin_client = KafkaAdminClient(bootstrap_servers='kafka:9092')
    
    try:
        admin_client.delete_topics([topic])
        print(f'Topic {topic} deleted successfully')
    except Exception as e:
        print(f'Failed to delete topic {topic}: {e}')
        sys.exit(1)
    finally:
        admin_client.close()

if __name__ == '__main__':
    topic_name = 'new_topic'
    

    # Create the topic (you can comment this out after the first run)
    create_topic(topic_name)

    # Produce a message
    produce_message(topic_name, 'Hello, Kafka!')

    # Consume messages (run in a separate terminal or concurrently)
    consume_messages(topic_name)

    # Delete topic
    delete_topic(topic_name)
    sys.exit()
