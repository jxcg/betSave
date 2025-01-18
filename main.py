from src.engine import Wager
from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_dance.contrib.google import make_google_blueprint, google
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

import math
import os
import yaml
import datetime



os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app             = Flask(__name__)
app.secret_key  = os.urandom(24)

def sanitise_floats(value, d=0.00):
    try:
        return float(value)
    except (TypeError, ValueError):
        return d


def read_config():
    with open("config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config

config = read_config()

# google blueprint object
google_blueprint = make_google_blueprint(

    client_id       = config['secrets']['client_id'],
    client_secret   = config['secrets']['client_secret'],
    scope           = ["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
    redirect_url    = 'http://localhost:5001/'

)

app.register_blueprint(google_blueprint, url_prefix="/login")
# SQLite "sqlite:///bets.db"
app.config["SQLALCHEMY_DATABASE_URI"]           = config['database']['uri']
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]    = False
db                                              = SQLAlchemy(app)


class Bet(db.Model):
    __tablename__ = "bets"
    id = db.Column(db.Integer, primary_key=True)
    back_stake              = db.Column(db.Float, default=0.00)
    lay_stake               = db.Column(db.Float, default=0.00)
    back_odds               = db.Column(db.Float, default=0.00)
    lay_odds                = db.Column(db.Float, default=0.00)
    user_email              = db.Column(db.String(255), nullable=False)
    bet_date                = db.Column(db.String, nullable=False)
    bet_type                = db.Column(db.String(255), default="Qualifying")
    profit_loss_bookie      = db.Column(db.Float, default=0.00)
    profit_loss_exchange    = db.Column(db.Float, default=0.00)
    event                   = db.Column(db.String(255))
    exchange                = db.Column(db.String(255))
    bookie                  = db.Column(db.String(255))
    back_commission         = db.Column(db.String(255))
    lay_commission          = db.Column(db.String(255))



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
    print("deleting:", bet_id)
    user_email = get_user_email(google.authorized)
    if not user_email:
        return redirect(url_for("google.login"))
    bet = Bet.query.get_or_404(bet_id)
    if bet.user_email != user_email:
        return "Unauthorized", 403

    db.session.delete(bet)
    db.session.commit()

    return redirect(url_for("tracker_page"))


@app.route("/edit_bet/<int:bet_id>", methods=["POST"])
def edit_bet(bet_id):
    print("editing:", bet_id)
    user_email = get_user_email(google.authorized)

    if not user_email: return redirect(url_for("google.login"))
    
    bet = Bet.query.get_or_404(bet_id)
    if bet.user_email != user_email: return "Unauthorized", 403

    db.session.delete(bet)
    db.session.commit()
    return redirect(url_for("tracker_page"))


@app.route("/tracker", methods=["GET", "POST"])
def tracker_page():
    free_bet_condition = False
    if not google.authorized:
        return redirect(url_for("google.login"))

    user_email = get_user_email(google.authorized)
    
    if request.method == "POST":

        # extract form data
        result          = request.form
        print(result)
        bet_date        = request.form.get("bet_date","").strip()
        bet_type        = request.form.get("bet_type","Qualifying").strip()
        bookie          = request.form.get("bookie_name").strip()
        exchange        = request.form.get("exchange_name").strip()
        event           = request.form.get("event_name").strip()
        back_odds       = request.form.get("back_odds").strip()
        lay_odds        = request.form.get("lay_odds").strip()
        back_stake      = request.form.get("back_stake").strip()
        back_commission = request.form.get("back_commission").strip()
        lay_commission  = request.form.get("lay_commission").strip()

        if not back_odds:
            back_odds   = sanitise_floats(back_odds)

        if not lay_odds:
            lay_odds    = sanitise_floats(lay_odds)

        if not bet_date:
            bet_date    = str(datetime.date.today())

        if bet_type == "Free":
            free_bet_condition = True
        
        wager_object = Wager(float(back_stake), float(back_odds), 0, 0, float(lay_odds), free_bet_condition)

        
        ## CALCULATE LAY STAKE automatically


        user_bet = Bet(
            user_email      = user_email,
            bookie          = bookie,
            back_odds       = back_odds,
            back_stake      = back_stake,
            lay_odds        = lay_odds,
            lay_stake       = round(wager_object.get_lay_stake(free_bet_condition), 2),
            bet_date        = bet_date,
            bet_type        = bet_type,
            exchange        = exchange,
            event           = event,
            back_commission = back_commission,
            lay_commission  = lay_commission
        )

        db.session.add(user_bet)
        db.session.commit()
        print("bet added to db")
        return redirect(url_for("tracker_page"))


    """
    Query to get all bets from DB for the user
    """

    all_user_bets               = Bet.query.filter_by(user_email=user_email).all()
    total_cumulative_profit     = 0.0
    
    for bet in all_user_bets:
        total_cumulative_profit += (bet.profit_loss_exchange + bet.profit_loss_bookie)

    return render_template(
        "tracker.html",
        bets        = all_user_bets,
        total       = total_cumulative_profit,
        user_email  = user_email
    )


@app.route('/bet_form', methods=["POST"])
def handle_bet_form():
    action = request.form.get("action")
    pass

if __name__ == "__main__":
    with app.app_context():
        db.drop_all() # debug
        db.create_all()
    app.run(host='0.0.0.0', port=5001, debug=True)
    