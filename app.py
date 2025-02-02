import json

from flask import Flask, redirect, url_for, render_template, request, session, jsonify
from datetime import timedelta, datetime
from os import environ as env
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from functools import wraps

# Load environment variables
load_dotenv(find_dotenv())

app = Flask(__name__)
app.secret_key = env.get("SECRET_KEY", "apples")
app.debug = True

# Auth0 settings
AUTH_BASE_URL = "https://egonzalez-fs-ais-authzero.us.auth0.com"
CLIENT_ID = env.get("CLIENT_ID", "WWSF7IYifiJKt8QIDRbRT4h66IFyEOV2")
CLIENT_SECRET = env.get("CLIENT_SECRET", "b2h-tpCo38mAl0RdX809PwsS7Ise0JTbY3vl6c7NVK2rWLEhm7QDmJX4PxIxladw")

oauth = OAuth(app)
auth0 = oauth.register(
    name='auth0',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    api_base_url=AUTH_BASE_URL,
    access_token_url=f"{AUTH_BASE_URL}/oauth/token",
    authorize_url=f"{AUTH_BASE_URL}/authorize",
    client_kwargs={
        "scope": "openid profile email"
    },
    server_metadata_url=f"{AUTH_BASE_URL}/.well-known/openid-configuration"
)

app.config['SESSION_TYPE'] = "filesystem"


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


@app.route("/login")
def login():
    return auth0.authorize_redirect(redirect_uri=url_for("callback", _external=True))


@app.route("/")
def main_home():
    return render_template("landing.html")

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = auth0.authorize_access_token()
    session['user'] = auth0.get("userinfo").json()
    print(session['user'])
    return redirect("/home")


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for("main_home"))
        return f(*args, **kwargs)
    return decorated


@app.route('/home')
@requires_auth
def home():
    return render_template("home.html")


@app.route('/about')
@requires_auth
def about():
    return render_template("about.html")


@app.route('/team')
@requires_auth
def team():
    return render_template("team.html")


@app.route('/dashboard')
@requires_auth
def dashboard():
    user_info = session.get('user', {})
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template("dashboard.html", user=user_info, pretty=json.dumps(user_info, indent=4), date=current_date)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main_home'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
