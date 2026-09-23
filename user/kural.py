from flask import Flask, json, jsonify, request, redirect, render_template, session
from app import db
import random
import time
import uuid
from datetime import datetime
from ngram_model import get_model


class kural:
    def fetchKural(self):
        if request.method == "POST":
            select_adhigaram = request.form.get('select_adhigaram')
            adhigaram_data = db['adhigaram_data']
            query = {"adhigaram": select_adhigaram}
            adhigaram = adhigaram_data.find(
                query, {"_id": 0, "adhigaram_id": 1})
            adhigaram_list = list(adhigaram)
            return jsonify({"adhigaram_id": adhigaram_list[0]["adhigaram_id"]}), 200

    def learn_thirukkural(self):
        if request.method == "GET":
            kuralId = request.args.get("kuralId")
            kural_data = db['kural_data']
            query = {"kural_id": int(kuralId)}
            return render_template('learn_thirukkural.html', kural=kural_data.find_one(query))

    def kural_yutham(self):
        if request.method == "GET":
            kuralId = request.args.get("kuralId")
            if not kuralId:
                kuralId = random.randint(1, 1330)
            kural_data = db['kural_data']
            query = {"kural_id": int(kuralId)}
            return render_template('kural_yutham.html', kural=kural_data.find_one(query))


    def selected_game(self):
        if request.method == "POST":
            select_adhigaram = request.form.get('select_adhigaram')
            random_kural = request.form.get('random_kural')
            game_type = request.form.get('game_type')
            error = ''
            if((select_adhigaram == '' and random_kural == None) or game_type == None):

                if(game_type == None):
                    error = '*விளையாட்டை தேர்வுசெய்க '
                else:
                    error = '*அதிகாரம் தேர்வுசெய்க'
                return jsonify({"error": error}), 401
            
            adhigaramNumber = 0
            if(random_kural != None):
                adhigaramNumber = random.randint(1, 133)

            elif(select_adhigaram != ''):
                adhigaram_data = db['adhigaram_data']
                #select_adhigaram = select_adhigaram.strip()
                query = {"adhigaram": select_adhigaram}
                print(select_adhigaram)

                adhigaram = adhigaram_data.find(
                    query, {"_id": 0, "adhigaram_id": 1})
                adhigaram_list = list(adhigaram)
                print(adhigaram_list)
                #kuralStarList = session['user']['points']['stars']['kurals_completed'][int(adhigaram_list[0]["adhigaram_id"]-1)]
                adhigaramNumber = adhigaram_list[0]['adhigaram_id']
                # for star in kuralStarList:
                #     if star == 0:
                #         error = '*'+select_adhigaram + \
                #             ' அதிகாரத்திலுள்ள அணைத்து குறள்களையும் கற்ற பின் விளையாடலாம்'
                #         return jsonify({"error": error}), 401
            

            """adhigaram_data = db['adhigaram_data']
            query = {"adhigaram": select_adhigaram}
            adhigaram = adhigaram_data.find(
                query, {"_id": 0, "adhigaram_id": 1})
            adhigaram_list = list(adhigaram)
            print(adhigaram_list)
            adhigaramNumber = adhigaram_list[0]['adhigaram_id'] """
             #Calculate the correct Kural ID
            kural_start = (adhigaramNumber - 1) * 10 + 1
            kural_end = adhigaramNumber * 10
            kuralNumber = random.randint(kural_start, kural_end)


            query = {"kural_id": int(kuralNumber)}
            return jsonify({"kuralId": str(kuralNumber), "site": game_type}), 200

    def drag_drop_game(self):
        if request.method == "GET":
            kuralId = request.args.get("kuralId")
            kural_data = db['kural_data']
            query = {"kural_id": int(kuralId)}
            kuralData = kural_data.find_one(query)
            kuralWordsList = kuralData['kural'][0][0].split(
            ) + kuralData['kural'][1][0].split()
            random.shuffle(kuralWordsList)
            return render_template('drag_drop_game.html', kuralWord=kuralWordsList, porul=kuralData['porul'], kuralId=kuralId)

    def evaluate_drag_game(self):
        if request.method == "POST":
            userAssignedKural = []
            userAssignedKural.append(request.form.get("word1"))
            userAssignedKural.append(request.form.get("word2"))
            userAssignedKural.append(request.form.get("word3"))
            userAssignedKural.append(request.form.get("word4"))
            userAssignedKural.append(request.form.get("word5"))
            userAssignedKural.append(request.form.get("word6"))
            userAssignedKural.append(request.form.get("word7"))
            kuralId = request.form.get("kuralId")
            kural_data = db['kural_data']
            query = {"kural_id": int(kuralId)}
            kuralData = kural_data.find_one(query)
            kuralWordsList = kuralData['kural'][0][0].split(
            ) + kuralData['kural'][1][0].split()
            diamonds = 0
            correctOrder = 0
            if(userAssignedKural == kuralWordsList):
                diamonds = 3
            else:
                for i in range(0, 7):
                    if(userAssignedKural[i] == kuralWordsList[i]):
                        correctOrder += 1

                if(correctOrder > 0 and correctOrder <= 3):
                    diamonds = 1
                elif(correctOrder > 3 and correctOrder <= 6):
                    diamonds = 2
                else:
                    diamonds = 0

            if (diamonds > 0):
                adhigaram_number = str(int(kuralId) % 10)
                total = 0
                if (int(session['user']['points']['diamonds']['drag_drop'][int(adhigaram_number)]) < int(session['user']['points']['diamonds']['total']) + diamonds):
                    total = (int(session['user']['points']['diamonds']['total']) + diamonds) - int(
                        session['user']['points']['diamonds']['drag_drop'][int(adhigaram_number)])
                else:
                    total = int(session['user']['points']['diamonds']
                                ['drag_drop'][int(adhigaram_number)])
                condition = {'email': session['user']['email']}
                dataToBeUpdated = {
                    "points.diamonds.drag_drop."+adhigaram_number: diamonds, "points.diamonds.total": total}

                db.user_details.update_one(
                    condition, {"$set": dataToBeUpdated})

                session['user']['points']['diamonds']['total'] = total
                session['user']['points']['diamonds']['drag_drop'][int(
                    adhigaram_number)] = diamonds

                session.modified = True

            return render_template('drag_drop_game_1.html', kuralWord=(kuralWordsList), porul=kuralData['porul'], diamonds=diamonds)

    def fillups_game(self):
        if request.method == "GET":
            kuralId = request.args.get("kuralId")
            kural_data = db['kural_data']
            query = {"kural_id": int(kuralId)}
            kuralData = kural_data.find_one(query)
            kuralWordsList = kuralData['kural'][0][0].split(
            ) + kuralData['kural'][1][0].split()
            missingWordIndex = random.randint(0, 6)
            missingWord = kuralWordsList[missingWordIndex]
            kuralWordsList[missingWordIndex] = "__________"

            #adding more options
            options = ["நீடுவாழ்", "யாண்டும்", "தாள்சேர்ந்தார்க்", "இனிய", "பயன்என்று",
    "உளரென்று", "அன்போடு", "மணியினும்", "செல்வத்துள்", "சான்றோர்",
    "மிகுத்து", "பெருக்கல்", "கேடில்லை", "இல்லாள்தன்", "நாடொறும்",
    "மறந்தும்", "காதன்மை", "வாய்மை", "பொருட்டால்", "கேள்வி",
    "மாண்ட", "படிபொறை", "தம்மைப்", "உளராக", "இடும்பை",
    "சால்பின்", "துறந்தார்", "கொடியன", "நாணுடைமை", "விரும்பி",
    "குழவி", "அம்மா", "நுகர்வார்", "அறத்தான்", "மாண்பு",
    "தொடர்ந்து", "விளக்கம்", "முன்னேறல்", "நிலைமை", "ஒழுக்கம்",
    "பிறப்பொடு", "துன்பம்", "தோன்றும்", "உணர்ச்சி", "உயர்ச்சி",
    "அடக்கம்", "செல்வம்", "பெருமை", "நன்றி"]
            random.shuffle(options)
            options = options[:3]
            if missingWord not in options:
                options.append(missingWord)
            random.shuffle(options)
            return render_template('fillups_game.html', kuralWord=kuralWordsList, porul=kuralData['porul'], kuralId=kuralId, options=options, index=missingWordIndex)

    def evaluate_fillups_game(self):
        if request.method == "POST":
            kuralId = request.form.get("kuralId")
            answer = request.form.get("answer")
            answerIndex = request.form.get("index")

            kural_data = db['kural_data']
            query = {"kural_id": int(kuralId)}
            kuralData = kural_data.find_one(query)
            kuralWordsList = kuralData['kural'][0][0].split(
            ) + kuralData['kural'][1][0].split()
            diamonds = 0
            if(kuralWordsList[int(answerIndex)] == answer):
                diamonds = 2
                adhigaram_number = str(int(kuralId) % 10)

                if (int(session['user']['points']['diamonds']['fillups'][int(adhigaram_number)]) < int(session['user']['points']['diamonds']['total']) + diamonds):
                    total = (int(session['user']['points']['diamonds']['total']) + diamonds) - int(
                        session['user']['points']['diamonds']['fillups'][int(adhigaram_number)])
                else:
                    total = int(session['user']['points']['diamonds']
                                ['fillups'][int(adhigaram_number)])
                condition = {'email': session['user']['email']}

                dataToBeUpdated = {
                    "points.diamonds.fillups."+adhigaram_number: diamonds, "points.diamonds.total": total}

                db.user_details.update_one(
                    condition, {"$set": dataToBeUpdated})

                session['user']['points']['diamonds']['total'] = total
                session['user']['points']['diamonds']['fillups'][int(
                    adhigaram_number)] = diamonds

                session.modified = True

            return render_template('fillups_game_1.html', diamonds=diamonds)

    def ngram_game(self):
        """Render the N-gram prediction game page."""
        if request.method == "GET":
            return render_template('ngram_game.html')

    def get_ngram_kural(self):
        """Get a random kural with one word masked for the N-gram game."""
        if request.method == "GET":
            kural_data = db['kural_data']
            
            # Get random kural ID (1-1330)
            random_kural_id = random.randint(1, 1330)
            
            query = {"kural_id": int(random_kural_id)}
            kuralData = kural_data.find_one(query)
            
            if not kuralData:
                return jsonify({"error": "Kural not found"}), 404
            
            # Validate kural structure
            if 'kural' not in kuralData or len(kuralData['kural']) < 2:
                return jsonify({"error": "Invalid kural structure"}), 400
            
            # We'll present the full kural (both lines) and mask two words across the combined lines
            line1 = kuralData['kural'][0][0] if len(kuralData['kural'][0]) > 0 else ""
            line2 = kuralData['kural'][1][0] if len(kuralData['kural'][1]) > 0 else ""
            full_line = (line1 + ' ' + line2).strip()

            words = [w.strip() for w in full_line.split() if w.strip()]

            if len(words) < 2:
                return jsonify({"error": "Kural has insufficient words"}), 400

            # Choose two distinct indices to mask. Prefer avoiding first/last if possible
            possible_indices = list(range(len(words)))
            if len(words) > 4:
                avoid = {0, len(words)-1}
                possible_indices = [i for i in possible_indices if i not in avoid]

            masked_indices = random.sample(possible_indices, k=2 if len(possible_indices) >= 2 else 1)

            # Build masked display with underscores matching word length
            correct_words = {}
            for idx in masked_indices:
                correct_words[str(idx)] = words[idx]

            display_words = []
            for i, w in enumerate(words):
                if i in masked_indices:
                    display_words.append('_' * max(3, len(w)))
                else:
                    display_words.append(w)

            masked_line = ' '.join(display_words)

            # Use same random options pool as fillups_game for distractors
            options_pool = ["நீடுவாழ்", "யாண்டும்", "தாள்சேர்ந்தார்க்", "இனிய", "பயன்என்று",
    "உளரென்று", "அன்போடு", "மணியினும்", "செல்வத்துள்", "சான்றோர்",
    "மிகுத்து", "பெருக்கல்", "கேடில்லை", "இல்லாள்தன்", "நாடொறும்",
    "மறந்தும்", "காதன்மை", "வாய்மை", "பொருட்டால்", "கேள்வி",
    "மாண்ட", "படிபொறை", "தம்மைப்", "உளராக", "இடும்பை",
    "சால்பின்", "துறந்தார்", "கொடியன", "நாணுடைமை", "விரும்பி",
    "குழவி", "அம்மா", "நுகர்வார்", "அறத்தான்", "மாண்பு",
    "தொடர்ந்து", "விளக்கம்", "முன்னேறல்", "நிலைமை", "ஒழுக்கம்",
    "பிறப்பொடு", "துன்பம்", "தோன்றும்", "உணர்ச்சி", "உயர்ச்சி",
    "அடக்கம்", "செல்வம்", "பெருமை", "நன்றி"]

            options = {}
            for idx in masked_indices:
                pool = [w for w in options_pool if w != words[idx]]
                random.shuffle(pool)
                choices = pool[:3]
                choices.append(words[idx])
                random.shuffle(choices)
                options[str(idx)] = choices

            # Return full data including adhigaram/porul
            return jsonify({
                "kural_id": random_kural_id,
                "kural_lines": [line1, line2],
                "masked_line": masked_line,
                "masked_indices": masked_indices,
                "correct_words": correct_words,
                "options": options,
                "aadhigaram": kuralData.get('aadhigaram', ''),
                "porul": kuralData.get('porul', {})
            }), 200

    def ngram_predict(self):
        """Get machine prediction for the masked word using N-gram model."""
        if request.method == "POST":
            data = request.get_json()
            masked_line = data.get('masked_line', '')
            masked_indices = data.get('masked_indices', [])

            if not masked_line or not isinstance(masked_indices, (list, tuple)) or len(masked_indices) == 0:
                return jsonify({"error": "Invalid request"}), 400

            start_time = time.time()

            # Get the N-gram model and make predictions for each masked index
            model = get_model()
            predicted_words = model.predict_from_line(masked_line, masked_indices)

            elapsed_time_ms = int((time.time() - start_time) * 1000)

            return jsonify({
                "predictions": predicted_words or [],
                "machine_time_ms": elapsed_time_ms
            }), 200

    def submit_ngram_score(self):
        """Submit user score and save to MongoDB."""
        if request.method == "POST":
            data = request.get_json()
            # Get score data (support arrays for multiple masked words)
            kural_id = data.get('kural_id')
            correct_words = data.get('correct_words') or {}
            user_answers = data.get('user_answer') or []
            machine_predictions = data.get('machine_prediction') or []
            user_time_ms = data.get('user_time_ms', 0)
            machine_time_ms = data.get('machine_time_ms', 0)

            # Normalize to lists
            if not isinstance(user_answers, list):
                user_answers = [user_answers]
            if not isinstance(machine_predictions, list):
                machine_predictions = [machine_predictions]

            # Determine per-word correctness
            user_correct_flags = []
            machine_correct_flags = []
            # If correct_words is dict keyed by index strings, iterate by that order
            keys = list(correct_words.keys()) if isinstance(correct_words, dict) else []
            if keys:
                for i, k in enumerate(keys):
                    corr = correct_words.get(k, '').strip()
                    ua = (user_answers[i].strip() if i < len(user_answers) and user_answers[i] else '').strip()
                    ma = (machine_predictions[i].strip() if i < len(machine_predictions) and machine_predictions[i] else '').strip()
                    user_correct_flags.append(ua == corr)
                    machine_correct_flags.append(ma == corr)
            else:
                # Fallback: compare first entries
                corr = data.get('correct_word', '')
                ua = user_answers[0] if len(user_answers) > 0 else ''
                ma = machine_predictions[0] if len(machine_predictions) > 0 else ''
                user_correct_flags = [ua.strip() == corr.strip()]
                machine_correct_flags = [ma.strip() == corr.strip()]
            
            # Get user info from session
            user_email = session.get('user', {}).get('email', '')
            user_name = session.get('user', {}).get('name', '')
            
            # Create score document
            score_doc = {
                "_id": uuid.uuid4().hex,
                "user_email": user_email,
                "user_name": user_name,
                "kural_id": int(kural_id),
                "correct_words": correct_words,
                "user_answers": user_answers,
                "machine_predictions": machine_predictions,
                "user_correct_flags": user_correct_flags,
                "machine_correct_flags": machine_correct_flags,
                "user_time_ms": int(user_time_ms),
                "machine_time_ms": int(machine_time_ms),
                "timestamp": datetime.now()
            }
            
            # Save to MongoDB
            ngram_scores = db['ngram_game_scores']
            ngram_scores.insert_one(score_doc)
            
            # Aggregate correctness
            user_correct_all = all(user_correct_flags) if len(user_correct_flags) > 0 else False
            machine_correct_all = all(machine_correct_flags) if len(machine_correct_flags) > 0 else False

            return jsonify({
                "success": True,
                "user_correct": user_correct_all,
                "machine_correct": machine_correct_all
            }), 200

    def ngram_leaderboard(self):
        """Get leaderboard for N-gram game."""
        if request.method == "GET":
            ngram_scores = db['ngram_game_scores']
            
            # Get top 10 players by accuracy (user_correct count)
            pipeline = [
                {
                    "$match": {"user_correct": True}
                },
                {
                    "$group": {
                        "_id": "$user_email",
                        "user_name": {"$first": "$user_name"},
                        "total_correct": {"$sum": 1},
                        "avg_time_ms": {"$avg": "$user_time_ms"}
                    }
                },
                {
                    "$sort": {"total_correct": -1, "avg_time_ms": 1}
                },
                {
                    "$limit": 10
                }
            ]
            
            leaderboard = list(ngram_scores.aggregate(pipeline))
            
            # Format leaderboard
            formatted_leaderboard = []
            for idx, entry in enumerate(leaderboard, 1):
                formatted_leaderboard.append({
                    "rank": idx,
                    "user_name": entry.get('user_name', ''),
                    "total_correct": entry.get('total_correct', 0),
                    "avg_time_ms": int(entry.get('avg_time_ms', 0))
                })
            
            return jsonify({"leaderboard": formatted_leaderboard}), 200

    def get_kurals_grid(self):
        from flask import request, jsonify, session
        from app import db
        from user.models import normalize_user_data
        
        adhigaram_id = request.args.get('adhigaram_id')
        search_query = request.args.get('search', '').strip()
        page = int(request.args.get('page', 1))
        
        query = {}
        if adhigaram_id and adhigaram_id.isdigit():
            aid = int(adhigaram_id)
            kural_start = (aid - 1) * 10 + 1
            kural_end = aid * 10
            query["kural_id"] = {"$gte": kural_start, "$lte": kural_end}
        elif search_query:
            if search_query.isdigit():
                query["kural_id"] = int(search_query)
            else:
                query["$or"] = [
                    {"kural.0.0": {"$regex": search_query, "$options": "i"}},
                    {"kural.1.0": {"$regex": search_query, "$options": "i"}},
                    {"aadhigaram": {"$regex": search_query, "$options": "i"}}
                ]
        else:
            query["kural_id"] = {"$gte": (page - 1) * 10 + 1, "$lte": page * 10}
            
        kurals = list(db.kural_data.find(query, {"_id": 0}).sort("kural_id", 1))
        
        user_email = session.get('user', {}).get('email')
        user_data = db.user_details.find_one({"email": user_email}) if user_email else None
        if user_data:
            user_data = normalize_user_data(user_data)
        else:
            user_data = session.get('user', {})
            
        k_prog = user_data.get('kural_progress', {})
        
        results = []
        for k in kurals:
            kid_str = str(k['kural_id'])
            prog = k_prog.get(kid_str, {})
            
            r1 = prog.get('round1_completed', False)
            r2 = prog.get('round2_completed', False)
            r3 = prog.get('round3_completed', False)
            
            rounds_count = (1 if r1 else 0) + (1 if r2 else 0) + (1 if r3 else 0)
            
            if r3:
                status = "நிறைவடைந்தது"
            elif r1 or r2:
                status = "செயலில் உள்ளது"
            else:
                status = "தொடங்கப்படவில்லை"
                
            line1 = k['kural'][0][0] if 'kural' in k and len(k['kural']) > 0 and len(k['kural'][0]) > 0 else ""
            line2 = k['kural'][1][0] if 'kural' in k and len(k['kural']) > 1 and len(k['kural'][1]) > 0 else ""
            
            results.append({
                "kural_id": k['kural_id'],
                "aadhigaram": k.get('aadhigaram', ''),
                "line1": line1,
                "line2": line2,
                "status": status,
                "rounds_completed": rounds_count,
                "round1_completed": r1,
                "round2_completed": r2,
                "round3_completed": r3,
                "coins": prog.get('coins_earned', 0),
                "diamonds": prog.get('diamonds_earned', 0)
            })
            
        return jsonify({"success": True, "kurals": results}), 200

    def evaluate_choose_round(self):
        from flask import request, jsonify, session
        from app import db
        from user.models import normalize_user_data
        
        data = request.get_json() or request.form
        kural_id = str(data.get('kuralId'))
        selected_word = data.get('selected_word', '').strip()
        correct_word = data.get('correct_word', '').strip()
        
        is_correct = (selected_word == correct_word)
        
        user_email = session.get('user', {}).get('email')
        if not user_email:
            return jsonify({"error": "User not logged in"}), 401
            
        user = db.user_details.find_one({"email": user_email})
        user = normalize_user_data(user)
        
        k_prog = user.setdefault('kural_progress', {})
        k_data = k_prog.get(kural_id, {
            "round1_completed": False,
            "round2_completed": False,
            "round3_completed": False,
            "coins_earned": 0,
            "diamonds_earned": 0,
            "total_attempts": 0,
            "best_score": 0,
            "bonus_claimed": False
        })
        
        k_data["total_attempts"] = k_data.get("total_attempts", 0) + 1
        
        coins_rewarded = 0
        diamonds_rewarded = 0
        already_completed = k_data.get("round1_completed", False)
        
        if is_correct:
            if not already_completed:
                coins_rewarded = 1
                diamonds_rewarded = 0
                k_data["round1_completed"] = True
                k_data["coins_earned"] = k_data.get("coins_earned", 0) + 1
                k_data["diamonds_earned"] = k_data.get("diamonds_earned", 0) + 0
                
                user["coins"] += 1
                user["diamonds"] += 0
                user["xp"] += 1
                user["level"] = 1 + (user["xp"] // 100)
                user["points"]["stars"]["total"] = user["coins"]
                user["points"]["diamonds"]["total"] = user["diamonds"]
                
        user["stats"]["total_games_played"] = user["stats"].get("total_games_played", 0) + 1
        k_prog[kural_id] = k_data
        
        db.user_details.update_one(
            {"email": user_email},
            {"$set": {
                "coins": user["coins"],
                "diamonds": user["diamonds"],
                "xp": user["xp"],
                "level": user["level"],
                "stats": user["stats"],
                "kural_progress": user["kural_progress"],
                "points.stars.total": user["coins"],
                "points.diamonds.total": user["diamonds"]
            }}
        )
        session['user'] = user
        session.modified = True
        
        return jsonify({
            "success": True,
            "is_correct": is_correct,
            "score": 1 if is_correct else 0,
            "coins_rewarded": coins_rewarded,
            "diamonds_rewarded": diamonds_rewarded,
            "already_completed": already_completed,
            "round1_completed": k_data["round1_completed"],
            "round2_unlocked": k_data["round1_completed"]
        }), 200

    def evaluate_arrange_round(self):
        from flask import request, jsonify, session
        from app import db
        from user.models import normalize_user_data
        
        data = request.get_json() or {}
        kural_id = str(data.get('kuralId'))
        user_words = data.get('words', [])
        
        kural_record = db.kural_data.find_one({"kural_id": int(kural_id)})
        if not kural_record:
            return jsonify({"error": "Kural not found"}), 404
            
        correct_words = (kural_record['kural'][0][0] + " " + kural_record['kural'][1][0]).split()
        
        is_correct = (user_words == correct_words)
        mismatched_indices = []
        for i in range(min(len(user_words), len(correct_words))):
            if user_words[i] != correct_words[i]:
                mismatched_indices.append(i)
                
        user_email = session.get('user', {}).get('email')
        if not user_email:
            return jsonify({"error": "User not logged in"}), 401
            
        user = db.user_details.find_one({"email": user_email})
        user = normalize_user_data(user)
        
        k_prog = user.setdefault('kural_progress', {})
        k_data = k_prog.get(kural_id, {
            "round1_completed": False,
            "round2_completed": False,
            "round3_completed": False,
            "coins_earned": 0,
            "diamonds_earned": 0,
            "total_attempts": 0,
            "best_score": 0,
            "bonus_claimed": False
        })
        
        k_data["total_attempts"] = k_data.get("total_attempts", 0) + 1
        
        coins_rewarded = 0
        diamonds_rewarded = 0
        already_completed = k_data.get("round2_completed", False)
        
        arrange_score = max(0, min(7, 7 - len(mismatched_indices)))
        if not already_completed:
            coins_rewarded = arrange_score
            diamonds_rewarded = 0
            if is_correct:
                k_data["round2_completed"] = True
            k_data["coins_earned"] = k_data.get("coins_earned", 0) + arrange_score
            
            user["coins"] += arrange_score
            user["diamonds"] += 0
            user["xp"] += arrange_score
            user["level"] = 1 + (user["xp"] // 100)
            user["points"]["stars"]["total"] = user["coins"]
            user["points"]["diamonds"]["total"] = user["diamonds"]
                
        user["stats"]["total_games_played"] = user["stats"].get("total_games_played", 0) + 1
        k_prog[kural_id] = k_data
        
        db.user_details.update_one(
            {"email": user_email},
            {"$set": {
                "coins": user["coins"],
                "diamonds": user["diamonds"],
                "xp": user["xp"],
                "level": user["level"],
                "stats": user["stats"],
                "kural_progress": user["kural_progress"],
                "points.stars.total": user["coins"],
                "points.diamonds.total": user["diamonds"]
            }}
        )
        session['user'] = user
        session.modified = True
        
        arrange_score = max(0, 7 - len(mismatched_indices))
        return jsonify({
            "success": True,
            "is_correct": is_correct,
            "score": arrange_score,
            "correct_count": arrange_score,
            "mismatched_indices": mismatched_indices,
            "coins_rewarded": coins_rewarded,
            "diamonds_rewarded": diamonds_rewarded,
            "already_completed": already_completed,
            "round2_completed": k_data["round2_completed"],
            "round3_unlocked": k_data["round2_completed"]
        }), 200

    def evaluate_voice_round(self):
        from flask import request, jsonify, session
        from app import db
        from user.models import normalize_user_data
        from datetime import datetime
        
        data = request.get_json() or {}
        kural_id = str(data.get('kuralId'))
        accuracy = int(data.get('accuracy', 0))
        
        if accuracy >= 95:
            stars = 3
        elif accuracy >= 80:
            stars = 2
        elif accuracy >= 60:
            stars = 1
        else:
            stars = 0
            
        is_passed = (accuracy >= 60)
        
        user_email = session.get('user', {}).get('email')
        if not user_email:
            return jsonify({"error": "User not logged in"}), 401
            
        user = db.user_details.find_one({"email": user_email})
        user = normalize_user_data(user)
        
        k_prog = user.setdefault('kural_progress', {})
        k_data = k_prog.get(kural_id, {
            "round1_completed": False,
            "round2_completed": False,
            "round3_completed": False,
            "coins_earned": 0,
            "diamonds_earned": 0,
            "total_attempts": 0,
            "best_score": 0,
            "bonus_claimed": False
        })
        
        k_data["total_attempts"] = k_data.get("total_attempts", 0) + 1
        
        r1_score = int(data.get('r1_score', 1 if k_data.get("round1_completed") else 0))
        r2_score = int(data.get('r2_score', 7 if k_data.get("round2_completed") else 0))
        r3_score = min(7, max(0, int(round((accuracy / 100.0) * 7))))
        attempt_total_score = r1_score + r2_score + r3_score
        
        if attempt_total_score > k_data.get("best_score", 0):
            k_data["best_score"] = attempt_total_score
            
        user["stats"]["total_voice_challenges"] = user["stats"].get("total_voice_challenges", 0) + 1
        user["stats"]["accuracy_sum"] = user["stats"].get("accuracy_sum", 0) + accuracy
        user["stats"]["accuracy_count"] = user["stats"].get("accuracy_count", 0) + 1
        user["stats"]["total_games_played"] = user["stats"].get("total_games_played", 0) + 1
        
        coins_rewarded = 0
        diamonds_rewarded = 0
        bonus_coins = 0
        bonus_diamonds = 0
        badge_awarded = None
        already_completed = k_data.get("round3_completed", False)
        
        r3_words_correct = max(0, min(7, int(round((accuracy / 100.0) * 7))))
        
        if not already_completed:
            coins_rewarded = r3_words_correct
            diamonds_rewarded = 1 if is_passed else 0
            if is_passed:
                k_data["round3_completed"] = True
                k_data["completion_date"] = datetime.now().isoformat()
                user["stats"]["total_kurals_completed"] = user["stats"].get("total_kurals_completed", 0) + 1
                
            k_data["coins_earned"] = k_data.get("coins_earned", 0) + r3_words_correct
            k_data["diamonds_earned"] = k_data.get("diamonds_earned", 0) + diamonds_rewarded
            
            user["coins"] += r3_words_correct
            user["diamonds"] += diamonds_rewarded
            user["xp"] += r3_words_correct
            
        if k_data.get("round1_completed") and k_data.get("round2_completed") and k_data.get("round3_completed") and not k_data.get("bonus_claimed"):
            bonus_coins = 0
            bonus_diamonds = 1
            badge_awarded = "Kural Master"
            k_data["bonus_claimed"] = True
            k_data["diamonds_earned"] += 1
            user["diamonds"] += 1
            
            if "badges" not in user or not isinstance(user["badges"], list):
                user["badges"] = []
            if "Kural Master" not in user["badges"]:
                user["badges"].append("Kural Master")
                    
        user["level"] = 1 + (user["xp"] // 100)
        user["points"]["stars"]["total"] = user["coins"]
        user["points"]["diamonds"]["total"] = user["diamonds"]
        
        k_prog[kural_id] = k_data
        
        db.user_details.update_one(
            {"email": user_email},
            {"$set": {
                "coins": user["coins"],
                "diamonds": user["diamonds"],
                "xp": user["xp"],
                "level": user["level"],
                "badges": user["badges"],
                "stats": user["stats"],
                "kural_progress": user["kural_progress"],
                "points.stars.total": user["coins"],
                "points.diamonds.total": user["diamonds"]
            }}
        )
        session['user'] = user
        session.modified = True
        
        return jsonify({
            "success": True,
            "is_passed": is_passed,
            "stars": stars,
            "accuracy": accuracy,
            "r3_score": r3_score,
            "attempt_total_score": attempt_total_score,
            "best_score": k_data["best_score"],
            "coins_rewarded": coins_rewarded,
            "diamonds_rewarded": diamonds_rewarded,
            "bonus_coins": bonus_coins,
            "bonus_diamonds": bonus_diamonds,
            "badge_awarded": badge_awarded,
            "already_completed": already_completed,
            "round3_completed": k_data["round3_completed"],
            "all_rounds_completed": (k_data.get("round1_completed") and k_data.get("round2_completed") and k_data.get("round3_completed"))
        }), 200

