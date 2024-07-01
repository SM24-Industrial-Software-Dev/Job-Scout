from datetime import datetime, timezone
import isodate
from Tables import Tables, Task, Mode
from botocore.exceptions import ClientError




class Scheduler:

    def __init__(self):
        self.table_set = Tables()
        self.segment = 0
        self.initialize_tables()

    def initialize_tables(self):
        self.table_set.initialize_tables()

    def add_task(self, t: Task):
        try:
            self.table_set.tasks.put_item(
                Item={
                    'task_id': t.task_id,
                    'user_id': t.user_id,
                    'mode': t.mode,
                    'recurring': t.recurring,
                    'interval': t.interval,
                    'retries': t.retries,
                    'created': t.created
                }
            )

            self.table_set.executions.put_item(
                Item={
                    'task_id': t.task_id,
                    'next_exec_time': datetime.now() + isodate.parse_duration(t.interval),
                    'segment': self.get_next_segment()
                }
            )

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
        return self.segment
         
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

if __name__ == "__main__":
    print("main is running")
    scheduler = Scheduler()
