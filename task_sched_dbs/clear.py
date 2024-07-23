from task_sched_dbs.delete_tables import delete_tables
from task_sched_dbs.delete_queues import delete_aws_resources
import time

delete_aws_resources()
delete_tables()
print("\033[93mloading... 20 seconds remaining... \033[0m")
time.sleep(20)
