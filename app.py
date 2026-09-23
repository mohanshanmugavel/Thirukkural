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


from user.models import normalize_user_data, update_user_streak

def compute_leaderboard_list(filter_type="global"):
    try:
        users = list(db.user_details.find({}, {"_id": 0, "password": 0}))
        leaderboard_list = []
        for u in users:
            u = normalize_user_data(u)
            name = u.get("name", "பயனர்")
            email = u.get("email", "")
            coins = u.get("coins", 0)
            diamonds = u.get("diamonds", 0)
            xp = u.get("xp", coins + (diamonds * 2))
            level = u.get("level", 1 + (xp // 100))
            
            k_prog = u.get("kural_progress", {})
            completed_count = sum(1 for k, v in k_prog.items() if isinstance(v, dict) and v.get("round3_completed"))
            if completed_count == 0:
                completed_list = u.get("points", {}).get("stars", {}).get("kurals_completed", [])
                if isinstance(completed_list, list):
                    for adhigaram in completed_list:
                        if isinstance(adhigaram, list):
                            for star in adhigaram:
                                if star and int(star) > 0:
                                    completed_count += 1
            
            streak_obj = u.get("streak", {})
            curr_streak = streak_obj.get("current_streak", 0)
            
            leaderboard_list.append({
                "name": name,
                "email": email,
                "coins": coins,
                "diamonds": diamonds,
                "xp": xp,
                "level": level,
                "points": coins + diamonds,
                "completed_count": completed_count,
                "streak": curr_streak
            })
            
        leaderboard_list.sort(key=lambda x: (x["xp"], x["completed_count"], x["coins"]), reverse=True)
        for idx, entry in enumerate(leaderboard_list, start=1):
            entry["rank"] = f"#{idx}"
        return leaderboard_list
    except Exception as e:
        print("Error computing leaderboard:", e)
        return []

def get_dashboard_data():
    curr_user = session.get("user", {})
    if curr_user and curr_user.get("email"):
        update_user_streak(curr_user["email"])
        db_user = db.user_details.find_one({"email": curr_user["email"]})
        if db_user:
            session["user"] = normalize_user_data(db_user)
            curr_user = session["user"]
            
    leaderboard_all = compute_leaderboard_list("global")
    leaderboard_top = leaderboard_all[:5]
    
    k_prog = curr_user.get("kural_progress", {})
    completed_count = sum(1 for k, v in k_prog.items() if isinstance(v, dict) and v.get("round3_completed"))
    if completed_count == 0:
        completed_list = curr_user.get("points", {}).get("stars", {}).get("kurals_completed", [])
        if isinstance(completed_list, list):
            for adhigaram in completed_list:
                if isinstance(adhigaram, list):
                    for star in adhigaram:
                        if star and int(star) > 0:
                            completed_count += 1

    streak_obj = curr_user.get("streak", {})
    current_streak = streak_obj.get("current_streak", 0)
    longest_streak = streak_obj.get("longest_streak", 0)
    progress_pct = int((completed_count % 10) * 10) if completed_count > 0 else 0

    return {
        "leaderboard": leaderboard_top,
        "completed_kural": completed_count,
        "streak": current_streak,
        "longest_streak": longest_streak,
        "progress_pct": progress_pct,
        "user_data": curr_user
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


@app.route('/play_kural')
@login_required
def play_kural():
    from flask import request
    kural_id = request.args.get('kuralId', 1)
    try:
        kural_id = int(kural_id)
    except Exception:
        kural_id = 1
        
    kural_record = db.kural_data.find_one({"kural_id": kural_id})
    if not kural_record:
        kural_record = db.kural_data.find_one({"kural_id": 1})
        
    user_email = session.get('user', {}).get('email')
    user_data = db.user_details.find_one({"email": user_email}) if user_email else None
    if user_data:
        user_data = normalize_user_data(user_data)
        session['user'] = user_data
    else:
        user_data = session.get('user', {})
        
    k_progress = user_data.get('kural_progress', {}).get(str(kural_id), {
        "round1_completed": False,
        "round2_completed": False,
        "round3_completed": False,
        "coins_earned": 0,
        "diamonds_earned": 0,
        "total_attempts": 0,
        "best_score": 0,
        "bonus_claimed": False
    })
    
    return render_template('play_kural.html', kural=kural_record, progress=k_progress)


@app.route('/profile')
@login_required
def profile():
    user_email = session.get('user', {}).get('email')
    user_data = db.user_details.find_one({"email": user_email}) if user_email else None
    if user_data:
        user_data = normalize_user_data(user_data)
        session['user'] = user_data
    else:
        user_data = session.get('user', {})
        
    k_prog = user_data.get('kural_progress', {})
    completed_count = sum(1 for k, v in k_prog.items() if isinstance(v, dict) and v.get("round3_completed"))
    
    stats = user_data.get('stats', {})
    acc_count = stats.get('accuracy_count', 0)
    acc_sum = stats.get('accuracy_sum', 0)
    avg_accuracy = int(acc_sum / acc_count) if acc_count > 0 else 0
    
    profile_data = {
        "user": user_data,
        "completed_count": completed_count,
        "completion_pct": round((completed_count / 1330.0) * 100, 1),
        "avg_accuracy": avg_accuracy
    }
    return render_template('profile.html', **profile_data)


@app.route('/api/leaderboard')
@login_required
def api_leaderboard():
    from flask import jsonify, request
    filter_type = request.args.get('filter', 'global')
    lb = compute_leaderboard_list(filter_type)
    return jsonify({"success": True, "leaderboard": lb[:5]})



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000)) 
    app.run(host="0.0.0.0", port=port)
