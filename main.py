import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Jobs')

def create_job(job_id, title, description, company, location):
    try:
        table.put_item(
            Item={
                'job_id': job_id,
                'title': title,
                'description': description,
                'company': company,
                'location': location
            }
        )
        print(f"Job {job_id} created successfully.")
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"Error: {str(e)}")

def get_job(job_id):
    try:
        response = table.get_item(
            Key={
                'job_id': job_id
            }
        )
        item = response.get('Item')
        if item:
            return item
        else:
            return f"Job {job_id} not found."
    except (NoCredentialsError, PartialCredentialsError) as e:
        return f"Error: {str(e)}"

def update_job(job_id, update_key, update_value):
    try:
        response = table.update_item(
            Key={
                'job_id': job_id
            },
            UpdateExpression=f"set #attr = :val",
            ExpressionAttributeNames={
                '#attr': update_key
            },
            ExpressionAttributeValues={
                ':val': update_value
            },
            ReturnValues="UPDATED_NEW"
        )
        return response
    except (NoCredentialsError, PartialCredentialsError) as e:
        return f"Error: {str(e)}"

def delete_job(job_id):
    try:
        response = table.delete_item(
            Key={
                'job_id': job_id
            }
        )
        return response
    except (NoCredentialsError, PartialCredentialsError) as e:
        return f"Error: {str(e)}"

# Example usage:
create_job('1', 'Software Engineer', 'Develop and maintain software.', 'Google', 'Boston')
print(get_job('1'))
update_job('1', 'location', 'New York')
print(get_job('1'))
delete_job("1")
print(get_job("1"))
