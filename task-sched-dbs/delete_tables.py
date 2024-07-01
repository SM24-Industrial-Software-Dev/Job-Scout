#Only for testing purposes
import boto3

# Initialize DynamoDB client
dynamodb = boto3.client('dynamodb', region_name='us-east-1')

# List of table names to delete
table_names = ['tasks', 'executions', 'history']

# Delete tables
for table_name in table_names:
    try:
        dynamodb.delete_table(TableName=table_name)
        print(f"Table {table_name} deleted successfully.")
    except dynamodb.exceptions.ResourceNotFoundException:
        print(f"Table {table_name} not found.")
    except Exception as e:
        print(f"Error deleting table {table_name}: {e}")
