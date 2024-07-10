import boto3
import json 

def setup_aws_resources():
    sns_client = boto3.client('sns')
    sqs_client = boto3.client('sqs')

    # Create SNS topics
    refresh_topic_arn = sns_client.create_topic(Name='refresh-topic')['TopicArn']
    notif_topic_arn = sns_client.create_topic(Name='notif-topic')['TopicArn']
    
    print(f"Created SNS topic for refresh: {refresh_topic_arn}")
    print(f"Created SNS topic for notif: {notif_topic_arn}")

    # Create SQS queues
    refresh_queue_url = sqs_client.create_queue(QueueName='refresh-queue')['QueueUrl']
    notif_queue_url = sqs_client.create_queue(QueueName='notif-queue')['QueueUrl']

    # Get the ARN of the SQS queues
    refresh_queue_arn = sqs_client.get_queue_attributes(QueueUrl=refresh_queue_url, AttributeNames=['QueueArn'])['Attributes']['QueueArn']
    notif_queue_arn = sqs_client.get_queue_attributes(QueueUrl=notif_queue_url, AttributeNames=['QueueArn'])['Attributes']['QueueArn']
    
    print(f"Created SQS queue for refresh: {refresh_queue_url} with ARN: {refresh_queue_arn}")
    print(f"Created SQS queue for notif: {notif_queue_url} with ARN: {notif_queue_arn}")

    # Define filter policies
    refresh_filter_policy = {
        'task_type': ['refresh']
    }
    
    notif_filter_policy = {
        'task_type': ['notif']
    }

    # Subscribe SQS queues to the SNS topics with filter policies
    sns_client.subscribe(
        TopicArn=refresh_topic_arn,
        Protocol='sqs',
        Endpoint=refresh_queue_arn,
        Attributes={
            'FilterPolicy': json.dumps(refresh_filter_policy)
        }
    )
    
    sns_client.subscribe(
        TopicArn=notif_topic_arn,
        Protocol='sqs',
        Endpoint=notif_queue_arn,
        Attributes={
            'FilterPolicy': json.dumps(notif_filter_policy)
        }
    )
    
    print(f"Subscribed {refresh_queue_arn} to {refresh_topic_arn} with filter policy: {json.dumps(refresh_filter_policy)}")
    print(f"Subscribed {notif_queue_arn} to {notif_topic_arn} with filter policy: {json.dumps(notif_filter_policy)}")

if __name__ == "__main__":
    setup_aws_resources()
