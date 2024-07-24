import boto3
from botocore.exceptions import ClientError
from datetime import datetime,timezone
# pylint: disable=no-name-in-module
# pylint: disable=no-self-argument
from pydantic import BaseModel, Field

def get_current_time() -> int:
        # Get current time as an integer timestamp rounded to the nearest minute
        now = datetime.now(timezone.utc)
        return get_unix_timestamp_by_min(now)

def get_unix_timestamp_by_min(dt: datetime) -> int:
    # Set seconds and microseconds to zero
    dt = dt.replace(second=0, microsecond=0)
    # Convert to UNIX timestamp
    return int(dt.timestamp())

class Task(BaseModel):
    task_id: int
    interval: str
    retries: int
    created: int= Field(default_factory=get_current_time) #int(datetime.now().timestamp()) #Field(default_factory=get_current_time)
    type: str

class Refresh(Task):
    last_refresh: int


class Notifs(Task):
    user_id: int
    email: str
    job_id: int = None
    title: str = None
    company: str = None
    location: str = None


class HistoryData(BaseModel):
    task_id: int
    exec_time: int
    status: str
    retries: int
    # last_update: int


class ExecutionsData(BaseModel):
    next_exec_time: int
    task_id: int
    segment: int


class Tables:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
        self.tasks = self.dynamodb.Table('tasks')
        self.executions = self.dynamodb.Table('executions')
        self.history = self.dynamodb.Table('history')

    def create_table(self, table_name, key_schema, attribute_definitions, provisioned_throughput, global_secondary_indexes=None):
        try:
            table_params = {
                'TableName': table_name,
                'KeySchema': key_schema,
                'AttributeDefinitions': attribute_definitions,
                'ProvisionedThroughput': provisioned_throughput
            }
            if global_secondary_indexes:
                table_params['GlobalSecondaryIndexes'] = global_secondary_indexes
            table = self.dynamodb.create_table(**table_params)
            table.wait_until_exists()
            print(f"\033[92mTable {table_name} created successfully.\033[0m")
        except Exception as e:
            print(f"\033[91mError creating table {table_name}: {e}\033[0m")

    def create_jobs_table(self, table_name='Jobs'):
        try:
            response = self.dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': 'job_id',
                        'KeyType': 'HASH'  # Partition key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'job_id',
                        'AttributeType': 'N'  # Number
                    },
                    {
                        'AttributeName': 'title',
                        'AttributeType': 'S'  # String
                    },
                    {
                        'AttributeName': 'company',
                        'AttributeType': 'S'  # String
                    },
                    {
                        'AttributeName': 'location',
                        'AttributeType': 'S'  # String
                    },
                    {
                        'AttributeName': 'link',
                        'AttributeType': 'S'  # String
                    },
                    {
                        'AttributeName': 'description',
                        'AttributeType': 'S'  # String
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            print(f"Job Table creation initiated. Status: {response['TableDescription']['TableStatus']}")
        except self.dynamodb.exceptions.ResourceInUseException:
            print(f"Table '{table_name}' already exists.")
        except ClientError as e:
            print(f"Error creating table: {str(e)}")


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
                    {'AttributeName': 'task_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'segment', 'KeyType': 'RANGE'}
                ],
                'attribute_definitions': [
                    {'AttributeName': 'segment', 'AttributeType': 'N'},
                    {'AttributeName': 'next_exec_time', 'AttributeType': 'N'},
                    {'AttributeName': 'task_id', 'AttributeType': 'N'}
                ],
                'provisioned_throughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5},
                'global_secondary_indexes': [
                    {
                        'IndexName': 'next_exec_time-task_id-index',
                        'KeySchema': [
                            {'AttributeName': 'next_exec_time', 'KeyType': 'HASH'}
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        }
                    }
                ]
            },
            'history': {
                'key_schema': [
                    {'AttributeName': 'task_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'exec_time', 'KeyType': 'RANGE'}
                ],
                'attribute_definitions': [
                    {'AttributeName': 'task_id', 'AttributeType': 'N'},
                    {'AttributeName': 'exec_time', 'AttributeType': 'N'},
                ],
                'provisioned_throughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            }
        }
        for table_name, table_config in tables.items():
            self.create_table(table_name,
                              table_config['key_schema'],
                              table_config['attribute_definitions'],
                              table_config['provisioned_throughput'],
                              table_config.get('global_secondary_indexes'))
        self.create_jobs_table()
            


if __name__ == "__main__":
    print("here comes main")
    table = Tables()
    table.initialize_tables()
