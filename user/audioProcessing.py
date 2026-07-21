from flask import Flask, render_template, request, redirect, session, jsonify
import speech_recognition as sr
from app import db

import wave
import difflib

class AudioProceesing:
    def practice(self):
        transcript = ""
        count = 0
        stars = 0

        if request.method == "POST":
            print("FORM DATA RECEIVED")

            if "file" not in request.files:
                return redirect(request.url)

            file = request.files["file"]
            if file.filename == "":
                return redirect(request.url)

            if file:
                recognizer = sr.Recognizer()
                audioFile = sr.AudioFile(file)
                with audioFile as source:
                    data = recognizer.record(source)
                transcript = recognizer.recognize_google(
                    data, language="ta-IN")

                spoken_words = []
                for i in transcript.split():
                    spoken_words.append(i)
                print(spoken_words)

                kuralId = request.form.get("getKuralId")
                kural_data = db['kural_data']
                query = {"kural_id": int(kuralId)}

                kural = kural_data.find_one(query)
                kuralWords = kural['kural'][0][0] + kural['kural'][1][0]

                for word in spoken_words:
                    if(word in kuralWords):
                        count += 1

                if(count > 0 and count <= 3):
                    stars = 1
                elif(count > 3 and count <= 6):
                    stars = 2
                elif(count == 7):
                    stars = 3
                else:
                    stars = 0

                adhigaram_number = str(int(kuralId) % 10 - 1)
                kural_number = str(int(kuralId)-1)
                total = (int(session['user']['points']['stars']['total']) + stars)
                - int(session['user']['points']['stars']['kurals_completed'][int(
                    adhigaram_number)][int(kural_number)])
                condition = {'email': session['user']['email']}

                dataToBeUpdated = {
                    "points.stars.kurals_completed."+adhigaram_number+"."+kural_number: stars, "points.stars.total": total
                }
                db.user_details.update_one(
                    condition, {"$set": dataToBeUpdated})

                session['user']['points']['stars']['total'] = total
                session['user']['points']['stars']['kurals_completed'][int(
                    adhigaram_number)][int(kural_number)] = stars
                session.modified = True

                return render_template('learn_thirukkural_1.html', stars=stars, count=count, kural=kural_data.find_one(query))

    def compareKural(self):
            transcript = ""
            count = 0
            stars = 0
            if request.method == "POST":
                f = request.files['audio_data']
                with open('audio.wav', 'wb') as audio:
                    f.save(audio)

                file = "audio.wav"
                recognizer = sr.Recognizer()
                audioFile = sr.AudioFile(file)
                print()
                with audioFile as source:
                    data = recognizer.record(source)
                transcript = recognizer.recognize_google(
                    data, language="ta-IN", show_all = True)
                if(not transcript ):
                    return  jsonify({"stars": 0, "count": 0}), 200
                spokenText = transcript['alternative'][0]['transcript']
                spoken_words = []
                for i in spokenText.split():
                    spoken_words.append(i)
                print(spoken_words)

                kuralId = request.form.get("getKuralId")


                
                kural_data = db['kural_data']
                query = {"kural_id": int(kuralId)}

                kural = kural_data.find_one(query)
                kural_words_original = (kural['kural'][0][0] + " " + kural['kural'][1][0]).split()
                
                import string
                kural_words_clean = [w.strip(string.punctuation) for w in kural_words_original]
                spoken_words_clean = [w.strip(string.punctuation) for w in spoken_words]

                kural_chars = "".join(kural_words_clean)
                spoken_chars = "".join(spoken_words_clean)

                expected_char_ranges = []
                curr_idx = 0
                for w in kural_words_clean:
                    expected_char_ranges.append((curr_idx, curr_idx + len(w)))
                    curr_idx += len(w)

                spoken_char_ranges = []
                curr_idx = 0
                for w in spoken_words_clean:
                    spoken_char_ranges.append((curr_idx, curr_idx + len(w)))
                    curr_idx += len(w)

                sm = difflib.SequenceMatcher(None, kural_chars, spoken_chars)
                opcodes = sm.get_opcodes()

                expected_char_matches = [0] * len(kural_chars)
                spoken_char_matches = [0] * len(spoken_chars)

                for tag, i1, i2, j1, j2 in opcodes:
                    if tag == 'equal':
                        for i in range(i1, i2): expected_char_matches[i] = 1
                        for j in range(j1, j2): spoken_char_matches[j] = 1

                word_statuses = []
                wrong_words = []
                missing_words = []
                correct_count = 0
                used_spoken_indices = set()

                for idx, (start, end) in enumerate(expected_char_ranges):
                    word_len = end - start
                    if word_len == 0:
                        word_statuses.append({"word": kural_words_original[idx], "status": "correct"})
                        correct_count += 1
                        continue
                    
                    matched = sum(expected_char_matches[start:end])
                    match_ratio = matched / word_len
                    
                    if match_ratio >= 0.8:
                        word_statuses.append({"word": kural_words_original[idx], "status": "correct"})
                        correct_count += 1
                    elif match_ratio == 0:
                        word_statuses.append({"word": kural_words_original[idx], "status": "missing"})
                        missing_words.append(kural_words_original[idx])
                    else:
                        word_statuses.append({"word": kural_words_original[idx], "status": "wrong"})
                        
                        # Find corresponding spoken words
                        said_word_indices = set()
                        for tag, i1, i2, j1, j2 in opcodes:
                            overlap_start = max(start, i1)
                            overlap_end = min(end, i2)
                            if overlap_start < overlap_end:
                                if tag in ('equal', 'replace'):
                                    sp_start = j1 + (overlap_start - i1)
                                    sp_end = sp_start + (overlap_end - overlap_start)
                                    for s_idx, (s_start, s_end) in enumerate(spoken_char_ranges):
                                        if max(sp_start, s_start) < min(sp_end, s_end):
                                            said_word_indices.add(s_idx)
                                elif tag == 'insert':
                                    if start <= i1 < end:
                                        for s_idx, (s_start, s_end) in enumerate(spoken_char_ranges):
                                            if max(j1, s_start) < min(j2, s_end):
                                                said_word_indices.add(s_idx)
                        
                        said_words_list = [spoken_words[i] for i in sorted(list(said_word_indices))]
                        used_spoken_indices.update(said_word_indices)
                        wrong_words.append({
                            "expected": kural_words_original[idx],
                            "said": " ".join(said_words_list) if said_words_list else ""
                        })

                extra_words = []
                for s_idx, (s_start, s_end) in enumerate(spoken_char_ranges):
                    word_len = s_end - s_start
                    if word_len == 0: continue
                    if sum(spoken_char_matches[s_start:s_end]) == 0 and s_idx not in used_spoken_indices:
                        extra_words.append(spoken_words[s_idx])

                total_words = len(kural_words_original)
                if correct_count > 0 and correct_count <= 3:
                    stars = 1
                elif correct_count > 3 and correct_count < total_words:
                    stars = 2
                elif correct_count == total_words:
                    stars = 3
                else:
                    stars = 0
                    
                accuracy = int((correct_count / total_words) * 100) if total_words > 0 else 0

                adhigaram_number = str(int(kuralId) % 10 - 1)
                kural_number = str(int(kuralId)-1)

                total = (int(session['user']['points']['stars']['total']) + stars)
                - int(session['user']['points']['stars']['kurals_completed'][int(
                    adhigaram_number)][int(kural_number)])
                condition = {'email': session['user']['email']}

                dataToBeUpdated = {
                    "points.stars.kurals_completed."+adhigaram_number+"."+kural_number: stars, "points.stars.total": total
                }
                db.user_details.update_one(
                    condition, {"$set": dataToBeUpdated})

                session['user']['points']['stars']['total'] = total
                session['user']['points']['stars']['kurals_completed'][int(
                    adhigaram_number)][int(kural_number)] = stars
                session.modified = True

                return jsonify({
                    "stars": stars,
                    "count": correct_count,
                    "total": total_words,
                    "accuracy": accuracy,
                    "spoken_text": spokenText,
                    "word_statuses": word_statuses,
                    "wrong_words": wrong_words,
                    "missing_words": missing_words,
                    "extra_words": extra_words
                }), 200
               
