from flask import Flask, render_template,redirect, session
from functools import wraps
import pymongo
import os
import ssl

app = Flask(__name__)
app.secret_key=b'\xf3\xc0\xcd\x1c\x147\x96C\xecf\xdf\x02H\x1c\xa6\xa6'



CONNECTION_STRING = os.getenv("STRING")
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.thirukkural_pazhagu

#Decorators
def login_required(f):
    @wraps(f)
    def wrap(*arg, **kwargs):
        if'logged_in' in session:
            return f(*arg, **kwargs)
        else:
            return redirect('/')
    return wrap

#Routes
from user import routes

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/register/')
def register():
    return render_template('register.html')


def get_dashboard_data():
    try:
        users = list(db.user_details.find({}, {"_id": 0, "name": 1, "points": 1}))
        leaderboard_list = []
        for u in users:
            name = u.get("name", "பயனர்")
            stars = u.get("points", {}).get("stars", {}).get("total", 0) or 0
            diamonds = u.get("points", {}).get("diamonds", {}).get("total", 0) or 0
            tot_points = int(stars) + int(diamonds)
            leaderboard_list.append({
                "name": name,
                "points": tot_points,
                "stars": stars,
                "diamonds": diamonds
            })
        leaderboard_list.sort(key=lambda x: x["points"], reverse=True)
        for idx, entry in enumerate(leaderboard_list, start=1):
            entry["rank"] = f"#{idx}"
        leaderboard = leaderboard_list[:5]
    except Exception as e:
        print("Error computing leaderboard:", e)
        leaderboard = []

    completed_count = 0
    curr_user = session.get("user", {})
    completed_list = curr_user.get("points", {}).get("stars", {}).get("kurals_completed", [])
    if isinstance(completed_list, list):
        for adhigaram in completed_list:
            if isinstance(adhigaram, list):
                for star in adhigaram:
                    if star and int(star) > 0:
                        completed_count += 1

    streak_days = max(1, completed_count // 2) if completed_count > 0 else 0
    progress_pct = int((completed_count % 10) * 10) if completed_count > 0 else 0

    return {
        "leaderboard": leaderboard,
        "completed_kural": completed_count,
        "streak": streak_days,
        "progress_pct": progress_pct
    }

@app.route('/index/')
@login_required
def index():    
    data = get_dashboard_data()
    return render_template('index.html', **data)


@app.route('/select_adhigaram')
@login_required
def select_adhigaram():
    return render_template('select_adhigaram.html')


@app.route('/select_game')
@login_required
def select_game():
    return render_template('select_game.html')


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000)) 
    app.run(host="0.0.0.0", port=port)
