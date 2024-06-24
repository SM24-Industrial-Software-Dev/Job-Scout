import os
from flask import Flask, redirect, url_for, session, request
from authlib.integrations.flask_client import OAuth




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
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri=app.config['GOOGLE_REDIRECT_URI'],
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account'
    }
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
    resp = google.get('userinfo')
    user_info = resp.json()
    session['user'] = user_info
    return f"Logged in as: {user_info['email']}"

if __name__ == '__main__':
    app.run('localhost', 5000, debug=True)