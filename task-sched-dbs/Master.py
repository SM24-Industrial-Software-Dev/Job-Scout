from datetime import datetime, timedelta, timezone
import boto3
import time
from Tables import Tables
from Scheduler import Scheduler, Refresh, Notifs, Task
import threading
import random

class Executer:
    def __init__(self, dynamodb, segment_start: int, segment_end: int):
        self.dynamodb = dynamodb
        self.segment_start = segment_start
        self.segment_end = segment_end
        self.executions_table = self.dynamodb.Table('executions')
        self.history_table = self.dynamodb.Table('history')

    def get_tasks(self, current_time):
        tasks = []
        for segment in range(self.segment_start, self.segment_end + 1):
            response = self.executions_table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('segment').eq(segment) &
                                       boto3.dynamodb.conditions.Key('next_exec_time').eq(current_time)
            )
            for item in response['Items']:
                task_id = int(item['task_id'])
                tasks.append(task_id)
        return tasks

    def process_tasks(self, current_time):
        tasks = self.get_tasks(current_time)
        #print("hey" + str(current_time))
        #if len(tasks) > 0:
            #print("hello")
        for task in tasks:
            self.publish_to_kafka(task)
            self.add_to_history_data(task, current_time, "success", 1)

            #print(task)

            ##In future, make it so we can just update the next_exec_time and not delete it##
            self.delete_execution_from_dynamodb(task, current_time)
            
    
    def delete_execution_from_dynamodb(self, task_id, next_exec_time):
        try:
            response = self.executions_table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('task_id').eq(task_id) &
                                 boto3.dynamodb.conditions.Attr('next_exec_time').eq(next_exec_time)
            )
            for item in response['Items']:
                self.executions_table.delete_item(
                    Key={
                        'next_exec_time': item['next_exec_time'],
                        'segment': item['segment']
                    }
                )
                print(f"Deleted task_id={task_id}, next_exec_time={next_exec_time} from executions table.")
        except Exception as e:
            print(f"Error deleting task_id={task_id}, next_exec_time={next_exec_time}: {e}")
    
    def add_to_history_data(self, task_id, exec_time, status, retries):
        # Convert task_id to int if necessary
        task_id = int(task_id)
        #print("woohoo")
        
        # Insert item into historydata table
        self.history_table.put_item(
            Item={
                'task_id': task_id,
                'exec_time': exec_time,
                'status': status,
                'retries': retries
            }
        )
        print(f"Added task_id={task_id} to historydata table with status '{status}' and {retries} retries.")

    def publish_to_kafka(self, task):
        # Placeholder logic for publishing task to Kafka
        print(f"Publishing task {task} to Kafka")


class Master:
    def __init__(self, schedule_instances:int = 1):
        self.scheduler = Scheduler()
        self.dyna = self.scheduler.table_set.dynamodb
        self.executer_count = (schedule_instances + 3) // 4  # This ensures ceil(schedule_instances / 4)
        if self.executer_count < 1:
            self.executer_count = 1
        
        self.executers = []
        
        # Create Executer instances with assigned ranges
        for i in range(self.executer_count):
            # Calculate segment ranges for each Executer
            min_seg = i * 4 + 1
            max_seg = min(min_seg + 3, schedule_instances)
            
            # Create Executer instance and add to list
            self.executers.append(Executer(self.dyna, min_seg, max_seg))
        

    def run(self):
        while True:
            current_time = self.get_current_time()
            self.update_executers(current_time)
            #print("current time: " + str(current_time))
            time.sleep(60)  # Sleep for 60 seconds

    def update_executers(self, current_time):
        for executer in self.executers:
            executer.process_tasks(current_time)

    def get_current_time(self) -> int:
        # Get current time as an integer timestamp rounded to the nearest minute
        now = datetime.now(timezone.utc)
        return self.get_unix_timestamp_by_min(now)

    def get_unix_timestamp_by_min(self, dt: datetime) -> int:
        # Set seconds and microseconds to zero
        dt = dt.replace(second=0, microsecond=0)
        # Convert to UNIX timestamp
        return int(dt.timestamp())

def run_master_in_background(master):
    master.run()

if __name__ == "__main__":
    print("Starting Master...")
    master = Master()
    sched = master.scheduler
    
    # Create a thread for running master.run() in the background
    master_thread = threading.Thread(target=run_master_in_background, args=(master,))
    master_thread.daemon = True  # Set daemon to True so it exits when the main thread exits
    master_thread.start()

    # Now continue with your main scheduler logic, receiving tasks and updating databases
    print("Running Scheduler and Receiving Tasks...")
    while True:
        rando = random.randint(1,10000)
        # Your scheduler logic to receive new tasks and update databases
        new_task = Refresh(
            task_id=rando,
            recurring=True,
            interval="PT1M",
            retries=3,
            created=int(datetime.now().timestamp()),
            last_refresh=0,
            type = "refresh"
        )
        sched.add_task(new_task)
        
