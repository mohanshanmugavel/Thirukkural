from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256
import uuid
from datetime import date

def normalize_user_data(user):
    if not user:
        return user
    
    if 'coins' not in user:
        user['coins'] = int(user.get('points', {}).get('stars', {}).get('total', 0) or 0)
    if 'diamonds' not in user:
        user['diamonds'] = int(user.get('points', {}).get('diamonds', {}).get('total', 0) or 0)
    if 'xp' not in user:
        user['xp'] = user['coins'] + (user['diamonds'] * 2)
    if 'level' not in user:
        user['level'] = 1 + (user['xp'] // 100)
    if 'badges' not in user:
        user['badges'] = []
    
    if 'streak' not in user or not isinstance(user['streak'], dict):
        user['streak'] = {
            "current_streak": 0,
            "longest_streak": 0,
            "last_active_date": None,
            "last_reward_day": 0
        }
    
    if 'stats' not in user or not isinstance(user['stats'], dict):
        user['stats'] = {
            "total_kurals_completed": 0,
            "total_games_played": 0,
            "total_voice_challenges": 0,
            "accuracy_sum": 0,
            "accuracy_count": 0
        }
        
    if 'kural_progress' not in user or not isinstance(user['kural_progress'], dict):
        user['kural_progress'] = {}
        
    if 'points' not in user:
        user['points'] = {}
    if 'stars' not in user['points']:
        user['points']['stars'] = {'total': user['coins'], 'kurals_completed': [[0 for _ in range(10)] for _ in range(133)]}
    else:
        user['points']['stars']['total'] = user['coins']
        
    if 'diamonds' not in user['points']:
        user['points']['diamonds'] = {'total': user['diamonds'], 'drag_drop': [0 for _ in range(133)], 'fillups': [0 for _ in range(133)]}
    else:
        user['points']['diamonds']['total'] = user['diamonds']

    return user

def update_user_streak(user_email):
    if not user_email:
        return
    from app import db
    user = db.user_details.find_one({"email": user_email})

    if not user:
        return
    
    user = normalize_user_data(user)
    today_str = date.today().isoformat()
    streak_data = user.get('streak', {})
    last_active = streak_data.get('last_active_date')
    current_streak = streak_data.get('current_streak', 0)
    longest_streak = streak_data.get('longest_streak', 0)
    last_reward_day = streak_data.get('last_reward_day', 0)
    
    daily_rewards_coins = [5, 10, 15, 20, 25, 30, 50]
    daily_rewards_diamonds = [0, 0, 0, 0, 0, 0, 5]
    
    coins_added = 0
    diamonds_added = 0
    
    if not last_active:
        current_streak = 1
        longest_streak = max(1, longest_streak)
        last_reward_day = 1
        coins_added = daily_rewards_coins[0]
        diamonds_added = daily_rewards_diamonds[0]
        last_active = today_str
    elif last_active == today_str:
        pass
    else:
        try:
            last_dt = date.fromisoformat(last_active)
            diff = (date.today() - last_dt).days
            if diff == 1:
                current_streak += 1
                longest_streak = max(current_streak, longest_streak)
                reward_idx = (current_streak - 1) % 7
                last_reward_day = reward_idx + 1
                coins_added = daily_rewards_coins[reward_idx]
                diamonds_added = daily_rewards_diamonds[reward_idx]
            else:
                current_streak = 1
                longest_streak = max(1, longest_streak)
                last_reward_day = 1
                coins_added = daily_rewards_coins[0]
                diamonds_added = daily_rewards_diamonds[0]
        except Exception:
            current_streak = 1
            longest_streak = max(1, longest_streak)
            last_reward_day = 1
            coins_added = daily_rewards_coins[0]
            diamonds_added = daily_rewards_diamonds[0]
            
        last_active = today_str

    new_coins = user['coins'] + coins_added
    new_diamonds = user['diamonds'] + diamonds_added
    new_xp = user['xp']
    new_level = 1 + (new_xp // 100)
    
    streak_obj = {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "last_active_date": last_active,
        "last_reward_day": last_reward_day
    }
    
    db.user_details.update_one(
        {"email": user_email},
        {"$set": {
            "streak": streak_obj,
            "coins": new_coins,
            "diamonds": new_diamonds,
            "xp": new_xp,
            "level": new_level,
            "points.stars.total": new_coins,
            "points.diamonds.total": new_diamonds
        }}
    )
    
    if session.get('user') and session['user'].get('email') == user_email:
        session['user']['streak'] = streak_obj
        session['user']['coins'] = new_coins
        session['user']['diamonds'] = new_diamonds
        session['user']['xp'] = new_xp
        session['user']['level'] = new_level
        session['user']['points']['stars']['total'] = new_coins
        session['user']['points']['diamonds']['total'] = new_diamonds
        session.modified = True


class User:
    def start_session(self, user):
        if 'password' in user:
            del user['password']
        user = normalize_user_data(user)
        session['logged_in'] = True
        session['user'] = user
        update_user_streak(user['email'])
        return jsonify(session['user']), 200

    def signup(self):
        kuralList = [[0 for _ in range(10)] for _ in range(133)]
        adhigaramList = [0 for _ in range(133)]
        
        user = {
            "_id": uuid.uuid4().hex,
            "name": request.form.get('name'),
            "email": request.form.get('email'),
            "password": request.form.get('password'),
            "cpassword": request.form.get('cpassword'),
            "coins": 0,
            "diamonds": 0,
            "xp": 0,
            "level": 1,
            "badges": [],
            "streak": {
                "current_streak": 0,
                "longest_streak": 0,
                "last_active_date": None,
                "last_reward_day": 0
            },
            "stats": {
                "total_kurals_completed": 0,
                "total_games_played": 0,
                "total_voice_challenges": 0,
                "accuracy_sum": 0,
                "accuracy_count": 0
            },
            "kural_progress": {},
            "points":{
                "stars":{
                    "total" : 0,
                    "kurals_completed": list(kuralList)
                },
                "diamonds":{
                    "total" : 0,
                    "drag_drop":list(adhigaramList),
                    "fillups":list(adhigaramList)
                }
            }
        }

        # Password Encryption
        user['password'] = pbkdf2_sha256.encrypt(user['password'])

        from app import db
        # check for existing email id
        if db.user_details.find_one({"email": user['email']}):
            return jsonify({"error": "Email already exists"}), 400

        if db.user_details.insert_one(user):
            return self.start_session(user)

        return jsonify({"error": "Signup failed"}), 400

    def signout(self):
        session.clear()
        return redirect('/')

    def delete_account(self):
        from app import db
        user_email = session.get('user', {}).get('email')
        if user_email:
            db.user_details.delete_one({"email": user_email})
            try:
                db.ngram_game_scores.delete_many({"user_email": user_email})
            except Exception:
                pass
        session.clear()
        return redirect('/')

    def login(self):
        from app import db
        user = db.user_details.find_one({"email": request.form.get('email')})

        if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
            return self.start_session(user)

        return jsonify({"error": "மின்னஞ்சல் அல்லது கடவுச்சொல் தவறு"}), 401


