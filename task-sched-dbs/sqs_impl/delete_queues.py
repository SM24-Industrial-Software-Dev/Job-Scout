import boto3

def delete_aws_resources():
    sns_client = boto3.client('sns', region_name='us-east-1')
    sqs_client = boto3.client('sqs', region_name='us-east-1')

    # List of topic and queue names to delete
    sns_topics = ['refresh-topic', 'notif-topic']
    sqs_queues = ['refresh-queue', 'notif-queue']

    # Your AWS region and account ID
    region = 'us-east-1'
    account_id = '339712802500'  # Account ID without hyphens

    # Delete SNS topics
    for topic_name in sns_topics:
        topic_arn = f'arn:aws:sns:{region}:{account_id}:{topic_name}'
        try:
            sns_client.delete_topic(TopicArn=topic_arn)
            print(f"\033[91mDeleted SNS topic: {topic_arn}\033[0m")
        except Exception as e:
            print(f"Error deleting SNS topic {topic_arn}: {e}")

    # Delete SQS queues
    for queue_name in sqs_queues:
        try:
            queue_url = sqs_client.get_queue_url(QueueName=queue_name)['QueueUrl']
            sqs_client.delete_queue(QueueUrl=queue_url)
            print(f"\033[91mDeleted SQS queue: {queue_url}\033[0m")
        except Exception as e:
            print(f"Error deleting SQS queue {queue_name}: {e}")

if __name__ == "__main__":
    delete_aws_resources()
