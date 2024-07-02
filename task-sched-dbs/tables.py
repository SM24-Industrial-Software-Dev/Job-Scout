from typing import Optional
from datetime import datetime

import boto3
from pydantic import BaseModel

class Task(BaseModel):
    task_id: int
    recurring: bool
    interval: str
    retries: int
    created: int
    type: str

class Refresh(Task):
    last_refresh: int

class Notifs(Task):
    user_id: int
    email: str
    job_id: int
    title: str
    description: str
    company: str
    location: str

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
                    {'AttributeName': 'task_id', 'KeyType': 'HASH'}
                ],
                'attribute_definitions': [
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
