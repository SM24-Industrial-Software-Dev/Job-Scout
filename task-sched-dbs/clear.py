from delete_tables import delete_tables
from sqs_impl.delete_queues import delete_aws_resources
import time

delete_aws_resources()
delete_tables()
print("\033[93mloading... 60 seconds remaining... \033[0m")
time.sleep(60)
