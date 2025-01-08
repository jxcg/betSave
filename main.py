from engine import calculate
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_dance.contrib.google import make_google_blueprint, google
import os
import yaml

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app = Flask(__name__)
app.secret_key = os.urandom(24)

def read_config():
    with open("config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config

config = read_config()

google_blueprint = make_google_blueprint(
    client_id=config['secrets']['client_id'],
    client_secret=config['secrets']['client_secret'],
    scope=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
    redirect_url='http://localhost:5001/'
)

app.register_blueprint(google_blueprint, url_prefix="/login")

@app.route("/get_started")
def get_started():
    if not google.authorized:
        # User is not logged in, go through OAuth
        return redirect(url_for("google.login"))
    else:
        # User is already logged in, send them to the landing page
        return redirect(url_for("landing_page"))


@app.route("/landing")
def landing_page():
    if not google.authorized:
        return redirect(url_for("google.login"))
    # user is authorized, so proceed
    return "Welcome to the Landing Page!"


@app.route("/logout")
def logout():
    """
    Clear the session (so google.authorized becomes False).
    """
    session.clear()
    return redirect(url_for("home"))


## Other Routes
@app.route("/")
def home():
    return render_template("index.html", title="Home")

@app.route("/calculate", methods=["POST"])
def calculate_route():
    try:
        bet_type = request.form['bet_type']
    except Exception as e:
        print(e)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)