from datetime import datetime, timedelta, timezone
import boto3
import time
from Tables import Tables
from Scheduler import Scheduler, Refresh, Notifs, Task
import threading

class Executer:
    def __init__(self, dynamodb, segment_start: int, segment_end: int):
        self.dynamodb = dynamodb
        self.segment_start = segment_start
        self.segment_end = segment_end
        self.executions_table = self.dynamodb.Table('executions')

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
        # Your scheduler logic to receive new tasks and update databases
        new_task = Refresh(
            task_id=1,
            recurring=True,
            interval="PT1M",
            retries=3,
            created=int(datetime.now().timestamp()),
            last_refresh=0,
            type = "refresh"
        )
        sched.add_task(new_task)
        
