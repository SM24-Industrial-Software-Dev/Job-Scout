import boto3
import json

class Impl:
    def __init__(self, refresh_topic_arn: str, notif_topic_arn: str):
        self.sns = boto3.client('sns')
        self.refresh_topic_arn = refresh_topic_arn
        self.notif_topic_arn = notif_topic_arn

    def send_message(self, message_body: dict, task_type: str):
        if task_type == 'refresh':
            topic_arn = self.refresh_topic_arn
        elif task_type == 'notif':
            topic_arn = self.notif_topic_arn
        else:
            raise ValueError("Unknown task type")

        response = self.sns.publish(
            TopicArn=topic_arn,
            Message=json.dumps(message_body)
        )
        print(f"Sent SNS message to {task_type} topic: {message_body}")
        return response