import os
import subprocess
import psutil
from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
import requests #changed

app = Flask(__name__)
app.secret_key = "CS_class_of_2027"

app.config['GOOGLE_ID'] = '197014094036-rbrpc7ot7nmkkj401809qbb1nheakeis.apps.googleusercontent.com'
app.config['GOOGLE_SECRET'] = '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'
app.config['GOOGLE_REDIRECT_URI'] = 'http://localhost:5000/callback'

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
    return 'Welcome.'

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/callback')
def authorize():
    token = google.authorize_access_token()
    resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
    user_info = resp.json()
    session['user'] = user_info
    
    fastapi_url = 'http://localhost:8000/register/'
    user_data = {
        "id": user_info["sub"],
        "email": user_info["email"],
        "name": user_info["name"]
    }
    request = requests.post(fastapi_url, json=user_data)
    if request.status_code !=200:
        print(f"Failed to register user: {request.text}")

    return redirect('http://localhost:8501')

@app.route('/streamlit')
def run_streamlit():
    user = session.get('user')
    if not user:
        return redirect('/login')
    
    # Check if Streamlit is already running
    if not any("streamlit" in p.name() for p in psutil.process_iter()):
        process = subprocess.Popen(
            ["streamlit", "run", "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            return f"Failed to start Streamlit: {stderr.decode()}"
    
    return redirect('http://localhost:8501')

if __name__ == '__main__':
    app.run('0.0.0.0', int(os.environ.get('PORT', 5000)), debug=True)
    