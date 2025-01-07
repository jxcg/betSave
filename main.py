from engine import calculate
from flask import Flask, render_template, redirect, url_for, flash, request
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



# Authentication
@app.route('/login/google')
def google_login():
    if not google.authorized:
        return redirect(url_for('google.login'))
    
    resp = google.get('/oauth2/v2/userinfo')
    if resp.ok:
        user_info = resp.json()
        print('ok')
        print(user_info)
        return f"You are {user_info['name']} or {email} on Google".format(email=resp.json()['email'])

    else:
        flash("Failed to log in with Google", category="error") 
        return redirect(url_for('home'))

@app.route("/protected")
def protected():
    if not google.authorized:
        return redirect(url_for("google.login"))
    # user is authorized, so proceed
    return "This is a protected page!"



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