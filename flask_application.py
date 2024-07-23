import os
import subprocess
import psutil
from flask import Flask, redirect, url_for, session, jsonify
from authlib.integrations.flask_client import OAuth
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)
app.secret_key = "CS_class_of_2027"

app.config['GOOGLE_ID'] = '197014094036-rbrpc7ot7nmkkj401809qbb1nheakeis.apps.googleusercontent.com'
app.config['GOOGLE_SECRET'] = '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'
app.config['GOOGLE_REDIRECT_URI'] = 'http://ec2-3-21-189-151.us-east-2.compute.amazonaws.com:8080/callback'

try:
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    users_table = dynamodb.Table('Users')
except ClientError as e:
    print(f"Error initializing DynamoDB: {e}")

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_ID'],
    client_secret=app.config['GOOGLE_SECRET'],
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    refresh_token_url=None,
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account'
    },
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)

@app.route('/')
def index():
    return 'You are currently not logged in.'

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/logout')
def logout():
    session.pop('user', None)
    # Redirect to app.py after logout
    return redirect('http://ec2-3-21-189-151.us-east-2.compute.amazonaws.com:8501')


@app.route('/callback')
def authorize():
    token = google.authorize_access_token()
    resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
    resp.raise_for_status()
    user_info = resp.json()
    session['user'] = user_info

    # Store user information in DynamoDB
    try:
        user_item = {
            'id': user_info['sub'],  # Assuming 'sub' is the unique identifier
            'email': user_info['email'],
            'name': user_info.get('name', ''),
            'preferred_job_type': None,
            'preferred_location': None
        }
        users_table.put_item(Item=user_item)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            # Handle case where user already exists (optional)
            pass
        else:
            print(f"Error storing user in DynamoDB: {e}")

    return redirect('http://ec2-3-21-189-151.us-east-2.compute.amazonaws.com:8502')  # Redirect to Streamlit logged_in_app.py

@app.route('/is_logged_in')
def is_logged_in():
    user = session.get('user')
    if user:
        return jsonify(logged_in=True, user=user)
    else:
        return jsonify(logged_in=False)

if __name__ == '__main__':
    app.run(port=8080)
