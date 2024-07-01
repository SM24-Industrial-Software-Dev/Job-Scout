from enum import Enum
from typing import Optional
from datetime import datetime

import boto3
from pydantic import BaseModel


class Mode(Enum):
    NOTIFS = "notifications"
    REFRESH = "refresh"

class Task(BaseModel):
    task_id: int
    user_id: int
    mode: str
    recurring: bool
    interval: str
    retries: int
    created: int

class HistoryData(BaseModel):
    task_id: int
    exec_time: int
    status: str
    retries: int
    last_update: int

class ExecutionsData(BaseModel):
    next_exec_time: int
    task_id: int
    segment: int

class Tables:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.tasks = self.dynamodb.Table('tasks')
        self.executions = self.dynamodb.Table('executions')
        self.history = self.dynamodb.Table('history')

    def create_table(self, table_name, key_schema, attribute_definitions, provisioned_throughput):
        try:
            table = self.dynamodb.create_table(
                TableName=table_name,
                KeySchema=key_schema,
                AttributeDefinitions=attribute_definitions,
                ProvisionedThroughput=provisioned_throughput
            )
            table.wait_until_exists()
            print(f"Table {table_name} created successfully.")
        except Exception as e:
            print(f"Error creating table {table_name}: {e}")

    def initialize_tables(self):
        tables = {
            'tasks': {
                'key_schema': [
                    {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'task_id', 'KeyType': 'RANGE'}
                ],
                'attribute_definitions': [
                    {'AttributeName': 'user_id', 'AttributeType': 'N'},
                    {'AttributeName': 'task_id', 'AttributeType': 'N'},
                ],
                'provisioned_throughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            },
            'executions': {
                'key_schema': [
                    {'AttributeName': 'segment', 'KeyType': 'HASH'},
                    {'AttributeName': 'next_exec_time', 'KeyType': 'RANGE'}
                ],
                'attribute_definitions': [
                    {'AttributeName': 'segment', 'AttributeType': 'N'},
                    {'AttributeName': 'next_exec_time', 'AttributeType': 'N'},
                ],
                'provisioned_throughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            },
            'history': {
                'key_schema': [
                    {'AttributeName': 'task_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'exec_time', 'KeyType': 'RANGE'}
                ],
                'attribute_definitions': [
                    {'AttributeName': 'task_id', 'AttributeType': 'N'},
                    {'AttributeName': 'exec_time', 'AttributeType': 'S'},
                ],
                'provisioned_throughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            }
        }
        for table_name, table_config in tables.items():
            self.create_table(table_name,
                              table_config['key_schema'],
                              table_config['attribute_definitions'],
                              table_config['provisioned_throughput'])
if __name__ == "__main__":
    print("here comes main")
    table = Tables()
    table.initialize_tables()
    new_task = Task(
        task_id=1,
        user_id=1,
        mode=Mode.NOTIFS,
        recurring=True,
        interval="PT10M",
        retries=3,
        created=int(datetime.now().timestamp())
    )
    print("here comes main 2")
    try:
        print("here comes main 3")
        table.tasks.put_item(
            Item={
                'task_id': new_task.task_id,
                'user_id': new_task.user_id,
                'mode': new_task.mode.value,  # Assuming mode needs to be the enum value
                'recurring': new_task.recurring,
                'interval': new_task.interval,
                'retries': new_task.retries,
                'created': new_task.created
            }
        )
        print(f"Task {new_task.task_id} added successfully.")
    except Exception as e:
        print("here comes main 3.5")
        print(f"Error adding task: {e}")
    print("here comes main 4")
