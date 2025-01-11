from src.engine import calculate
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_dance.contrib.google import make_google_blueprint, google
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

import os
import yaml
import datetime

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
# SQLite "sqlite:///bets.db"
app.config["SQLALCHEMY_DATABASE_URI"] = config['database']['uri']
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Bet(db.Model):
    __tablename__ = "bets"
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(255), nullable=False)
    bet_date = db.Column(db.String, nullable=False)
    bet_type = db.Column(db.String(255), default="Qualifying")
    profit_loss_bookie = db.Column(db.Float, default=0.0)
    profit_loss_exchange = db.Column(db.Float, default=0.0)
    event = db.Column(db.String(255))
    exchange = db.Column(db.String(255))
    bookie = db.Column(db.String(255))



    def __repr__(self): 
        return f"<Bet {self.id} - {self.user_email} - {self.bet_date}>"



def get_user_email(authed):
    if not authed:
        print("Not authed")
        return None

    if "user_email" not in session:
        print("Not in session")
        resp = google.get("/oauth2/v2/userinfo")
        if not resp.ok:
            return None
    
        user_info = resp.json()

        session['user_email'] = user_info['email']
        print(session['user_email'])
    return session['user_email']






# --------------------------------------------
# Routes
# --------------------------------------------

@app.route("/get_started")
def get_started():
    if not google.authorized:
        # User is not logged in, go through OAuth
        return redirect(url_for("google.login"))
    else:
        # User is already logged in, send them to the landing page
        return redirect(url_for("tracker_page"))


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


# --------------------------------------------
# Bet Tracking Routes
# --------------------------------------------

@app.route("/delete_bet/<int:bet_id>", methods=["POST"])
def delete_bet(bet_id):
    pass

@app.route("/tracker", methods=["GET", "POST"])
def tracker_page():
    if not google.authorized:
        return redirect(url_for("google.login"))
    # user is authorised, so proceed
    user_email = get_user_email(google.authorized)
    
    if request.method == "POST":
        # extract form data
        bet_date = request.form.get("bet_date","").strip()
        bet_type = request.form.get("bet_type","Qualifying")
        profit_loss_bookie = request.form.get("profit_loss_bookie","0")
        profit_loss_exchange = request.form.get("profit_loss_exchange","0")
        bookie = request.form.get("bookie_name")
        exchange = request.form.get("exchange_name")
        event = request.form.get("event_name")
        if not bet_date:
            bet_date = str(datetime.date.today())
        try:
            pl_bookie = float(profit_loss_bookie)
        except ValueError:
            pl_bookie = 0.0

        try:
            pl_exchange = float(profit_loss_exchange)
        except ValueError:
            pl_exchange = 0.0

        user_bet = Bet(
            user_email=user_email,
            bet_date=bet_date,
            bet_type=bet_type,
            profit_loss_bookie=pl_bookie,
            profit_loss_exchange=pl_exchange,
            bookie=bookie,
            exchange=exchange,
            event=event
        )

        db.session.add(user_bet)
        db.session.commit()
        return redirect(url_for("tracker_page"))

    all_user_bets = Bet.query.filter_by(user_email=user_email).all()

    total_cumulative_profit = 0.0
    for bet in all_user_bets:
        total_cumulative_profit += (bet.profit_loss_exchange + bet.profit_loss_bookie)

    return render_template(
        "tracker.html",
        bets=all_user_bets,
        total = total_cumulative_profit,
        user_email = user_email
    )

if __name__ == "__main__":
    with app.app_context():
        db.drop_all() # debug
        db.create_all()
    app.run(host='0.0.0.0', port=5001, debug=True)