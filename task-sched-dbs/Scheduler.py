from datetime import datetime
import isodate
from Tables import Tables, Task, Refresh, Notifs
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key




class Scheduler:

    def __init__(self, max_seg: int = 2):
        self.table_set = Tables()
        self.segment_max = max_seg
        self.segment = 0
        self.initialize_tables()

    def initialize_tables(self):
        self.table_set.initialize_tables()

    def add_task(self, t: Task):
        try:
            task_item={
                'task_id': t.task_id,
                'recurring': t.recurring,
                'interval': t.interval,
                'retries': t.retries,
                'created': self.get_unix_timestamp_by_min(datetime.fromtimestamp(t.created)),
                'type': t.type
            }
            # Handle specific task types
            if isinstance(t, Refresh):
                task_item['last_refresh'] = t.last_refresh
                
            elif isinstance(t, Notifs):
                task_item.update({
                    'user_id': t.user_id,
                    'email': t.email,
                    'job_id': t.job_id,
                    'title': t.title,
                    'description': t.description,
                    'company': t.company,
                    'location': t.location
                })
            else:
                raise UnknownTaskTypeError(t)
            self.table_set.tasks.put_item(Item=task_item)
            print("\033[94mtask " + str(t.task_id) + " added to tasks table!\033[0m")
            self.table_set.executions.put_item(
                Item={
                    'task_id': t.task_id,
                    'next_exec_time': self.get_unix_timestamp_by_min(datetime.now() + isodate.parse_duration(t.interval)),
                    'segment': self.get_next_segment()
                }
            )
            print("\033[94mtask " + str(t.task_id) + " added to EXECUTIONS table!\033[0m")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            print(f"Error putting item in DynamoDB: {error_code} - {error_message}")
            # Handle specific error cases here

        except Exception as e:
            print(f"Unexpected error: {e}")
            # Handle unexpected errors or log them for investigation

    def get_next_segment(self):
        self.segment += 1
        if self.segment >= self.segment_max:
            self.segment = 1
        return self.segment
    
    def set_segment(self, segment:int):
        self.segment=segment

    def set_max_segment(self, seg_max:int):
        self.segment_max=seg_max
         
    def query_executions_by_next_exec_time(self, next_exec_time):
        try:
            response = self.table_set.executions.query(
                KeyConditionExpression=Key('next_exec_time').eq(next_exec_time)
            )

            for item in response['Items']:
                print(item)  # Process each item as needed -- eventually return them so they can be executed

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            print(f"Error querying executions table: {error_code} - {error_message}")
            # Handle specific error cases here

        except Exception as e:
            print(f"Unexpected error: {e}")
            # Handle unexpected errors or log them for investigation

    def get_unix_timestamp_by_min(self, dt: datetime) -> int:
       
        # Set seconds and microseconds to zero

        dt = dt.replace(second=0, microsecond=0)

        # Convert to UNIX timestamp
        unix_timestamp = int(dt.timestamp())
        return unix_timestamp
    
    def convert_datetime_to_iso8601(self, dt: datetime) -> str:
        # Convert datetime to ISO 8601 string
        return dt.isoformat()

class UnknownTaskTypeError(Exception):
        def __init__(self, task: Task):
            super().__init__(f"Unknown task type for task: {task.task_id}")


##TEST CODE##
if __name__ == "__main__":
    print("Creating Scheduler...")
    scheduler = Scheduler()
    new_task = Refresh(
        task_id=1,
        recurring=True,
        interval="PT1M",
        retries=3,
        created=int(datetime.now().timestamp()),
        last_refresh=0,
        type = "refresh"
    )
    scheduler.add_task(new_task)
