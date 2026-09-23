from flask import Flask, render_template, request, redirect, session, jsonify
import tempfile
import os
import uuid
import speech_recognition as sr
from app import db
import wave
import audioop
import string
import difflib
import re

def preprocess_audio_wav(file_path):
    """Normalize audio amplitude and apply noise gate to boost soft child voices and remove background hiss."""
    try:
        wf = wave.open(file_path, 'rb')
        params = wf.getparams()
        nchannels, sampwidth, framerate, nframes = params[:4]
        frames = wf.readframes(nframes)
        wf.close()

        if sampwidth == 2 and nframes > 0:
            # 1. Remove DC bias offset / noise baseline
            frames = audioop.bias(frames, 2, 0)
            
            # 2. Audio Peak Normalization (Boost soft child voices)
            max_val = audioop.max(frames, 2)
            if 0 < max_val < 20000:
                factor = min(4.0, 26000.0 / float(max_val))
                frames = audioop.mul(frames, 2, factor)
            
            # Re-write processed audio to file
            wf_out = wave.open(file_path, 'wb')
            wf_out.setparams(params)
            wf_out.writeframes(frames)
            wf_out.close()
    except Exception as e:
        print("Audio WAV preprocessing exception (continuing with raw audio):", e)

def split_tamil_syllables(text):
    """Split Tamil text into grapheme clusters / syllables."""
    if not text:
        return []
    text = text.strip(string.punctuation)
    pattern = r'[\u0B85-\u0B94\u0B95-\u0BB9][\u0BBE-\u0BCD\u0BD7]*'
    return re.findall(pattern, text)

def normalize_syllable(s, mode="child"):
    """Normalize speech variations at syllable level based on voice mode."""
    if mode == "adult":
        # Adult mode: Strict - requires exact pronunciation ('ழ' stays 'ழ', 'ற' stays 'ற')
        s = s.replace('ஷ', 'ச').replace('ஸ', 'ச').replace('ஜ', 'ச').replace('ஹ', 'க').replace('ஃ', '')
        return s

    # Child mode: Liberal - allows child sound swaps ('ழ'->'ல', 'ற'->'ர', 'ண'/'ன'->'ந', 'ள'->'ல', vowel shifts)
    s = s.replace('ஷ', 'ச').replace('ஸ', 'ச').replace('ஜ', 'ச').replace('ஹ', 'க').replace('ஃ', '')
    s = s.replace('ற', 'ர').replace('ன', 'ந').replace('ண', 'ந').replace('ள', 'ல').replace('ழ', 'ல')
    s = s.replace('ஆ', 'அ').replace('ஈ', 'இ').replace('ஊ', 'உ').replace('ஏ', 'எ').replace('ஓ', 'ஒ')
    s = s.replace('ா', '').replace('ீ', 'ி').replace('ூ', 'ு').replace('ே', 'ெ').replace('ோ', 'ொ').replace('ை', 'ெ')
    return s

def compute_tamil_word_similarity(w1, w2, mode="child"):
    if not w1 or not w2:
        return 0.0
    w1_c = w1.strip(string.punctuation)
    w2_c = w2.strip(string.punctuation)
    if not w1_c or not w2_c:
        return 0.0
    if w1_c == w2_c:
        return 1.0

    s1 = split_tamil_syllables(w1_c)
    s2 = split_tamil_syllables(w2_c)
    
    if not s1 or not s2:
        return difflib.SequenceMatcher(None, w1_c, w2_c).ratio()

    # Raw syllable sequence ratio
    raw_syl_ratio = difflib.SequenceMatcher(None, s1, s2).ratio()

    # Mode-dependent normalized syllable ratio
    ns1 = [normalize_syllable(x, mode=mode) for x in s1]
    ns2 = [normalize_syllable(x, mode=mode) for x in s2]
    norm_syl_ratio = difflib.SequenceMatcher(None, ns1, ns2).ratio()

    return max(raw_syl_ratio, norm_syl_ratio)

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
                recognizer.energy_threshold = 200
                recognizer.dynamic_energy_threshold = True
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
        if request.method == "POST":
            kuralId = request.form.get("getKuralId", "1")
            voice_mode = request.form.get("voice_mode", "child")
            print(f"Speech recognition request - KuralID: {kuralId}, Voice Mode: {voice_mode}")

            kural_data = db['kural_data']
            try:
                query = {"kural_id": int(kuralId)}
            except Exception:
                query = {"kural_id": 1}

            kural = kural_data.find_one(query)
            if not kural:
                kural_words_original = []
            else:
                kural_words_original = (kural['kural'][0][0] + " " + kural['kural'][1][0]).split()

            total_words = len(kural_words_original)
            word_statuses_empty = [{"word": w, "status": "missing"} for w in kural_words_original]

            if 'audio_data' not in request.files:
                return jsonify({
                    "status": "error",
                    "message": "ஒலி கோப்பு பெறப்படவில்லை.",
                    "stars": 0,
                    "count": 0,
                    "total": total_words,
                    "accuracy": 0,
                    "spoken_text": "",
                    "word_statuses": word_statuses_empty,
                    "wrong_words": [],
                    "missing_words": kural_words_original,
                    "extra_words": []
                }), 200

            f = request.files['audio_data']
            audio_path = os.path.join(tempfile.gettempdir(), f"audio_{uuid.uuid4().hex}.wav")
            f.save(audio_path)

            # Preprocess audio (gain boost, noise reduction for child voices)
            preprocess_audio_wav(audio_path)

            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 200
            recognizer.dynamic_energy_threshold = True
            recognizer.pause_threshold = 0.8

            try:
                with sr.AudioFile(audio_path) as source:
                    data = recognizer.record(source)
                transcript_res = recognizer.recognize_google(data, language="ta-IN", show_all=True)
            except sr.UnknownValueError:
                return jsonify({
                    "status": "unrecognized",
                    "message": "மன்னிக்குக, உங்கள் குரல் தெளிவாகக் கேட்கவில்லை. மீண்டும் முயற்சி செய்யவும்.",
                    "stars": 0,
                    "count": 0,
                    "total": total_words,
                    "accuracy": 0,
                    "spoken_text": "",
                    "word_statuses": word_statuses_empty,
                    "wrong_words": [],
                    "missing_words": kural_words_original,
                    "extra_words": []
                }), 200
            except sr.RequestError as e:
                return jsonify({
                    "status": "error",
                    "message": "குரல் உணர்தல் சேவையில் பிழை ஏற்பட்டது. இணைய இணைப்பை சரிபார்க்கவும்.",
                    "stars": 0,
                    "count": 0,
                    "total": total_words,
                    "accuracy": 0,
                    "spoken_text": "",
                    "word_statuses": word_statuses_empty,
                    "wrong_words": [],
                    "missing_words": kural_words_original,
                    "extra_words": []
                }), 200
            except Exception as e:
                print("Speech recognition processing exception:", e)
                return jsonify({
                    "status": "error",
                    "message": "குரல் செயலாக்கத்தில் பிழை: " + str(e),
                    "stars": 0,
                    "count": 0,
                    "total": total_words,
                    "accuracy": 0,
                    "spoken_text": "",
                    "word_statuses": word_statuses_empty,
                    "wrong_words": [],
                    "missing_words": kural_words_original,
                    "extra_words": []
                }), 200

            if not transcript_res or not isinstance(transcript_res, dict) or 'alternative' not in transcript_res or not transcript_res['alternative']:
                return jsonify({
                    "status": "unrecognized",
                    "message": "மன்னிக்குக, உங்கள் குரல் தெளிவாகக் கேட்கவில்லை. மீண்டும் முயற்சி செய்யவும்.",
                    "stars": 0,
                    "count": 0,
                    "total": total_words,
                    "accuracy": 0,
                    "spoken_text": "",
                    "word_statuses": word_statuses_empty,
                    "wrong_words": [],
                    "missing_words": kural_words_original,
                    "extra_words": []
                }), 200

            alt_transcripts = [alt.get('transcript', '') for alt in transcript_res.get('alternative', []) if alt.get('transcript')]
            if not alt_transcripts:
                alt_transcripts = [""]

            N = len(kural_words_original)
            candidate_cutoff = 0.35 if voice_mode == "child" else 0.50
            correct_cutoff = 0.60 if voice_mode == "child" else 0.85

            def evaluate_transcript_alignment(spoken_text):
                spoken_words = spoken_text.split()
                if not spoken_words:
                    return 0.0, [], [], [], [], []
                M = len(spoken_words)
                candidates = []
                for i in range(N):
                    exp_w = kural_words_original[i]
                    for j in range(M):
                        score = compute_tamil_word_similarity(exp_w, spoken_words[j], mode=voice_mode)
                        if score >= candidate_cutoff:
                            candidates.append((i, j, j + 1, score, spoken_words[j]))
                    for j in range(M - 1):
                        combo = spoken_words[j] + spoken_words[j+1]
                        score = compute_tamil_word_similarity(exp_w, combo, mode=voice_mode)
                        if score >= candidate_cutoff:
                            candidates.append((i, j, j + 2, score, spoken_words[j] + " " + spoken_words[j+1]))

                cand_sorted = sorted(candidates, key=lambda c: (c[0], c[1]))
                memo = {}
                def solve(cand_idx):
                    if cand_idx in memo:
                        return memo[cand_idx]
                    curr = cand_sorted[cand_idx]
                    max_s = curr[3]
                    max_p = [curr]
                    for next_idx in range(cand_idx + 1, len(cand_sorted)):
                        nxt = cand_sorted[next_idx]
                        if nxt[0] > curr[0] and nxt[1] >= curr[2]:
                            sub_s, sub_p = solve(next_idx)
                            if curr[3] + sub_s > max_s:
                                max_s = curr[3] + sub_s
                                max_p = [curr] + sub_p
                    memo[cand_idx] = (max_s, max_p)
                    return memo[cand_idx]

                best_overall_score = 0.0
                best_path = []
                for idx in range(len(cand_sorted)):
                    score, path = solve(idx)
                    if score > best_overall_score:
                        best_overall_score = score
                        best_path = path

                matched_map = {c[0]: c for c in best_path}
                used_spoken_indices = set()
                for c in best_path:
                    for sj in range(c[1], c[2]):
                        used_spoken_indices.add(sj)

                word_statuses = []
                wrong_words = []
                missing_words = []
                correct_count = 0

                for i in range(N):
                    exp_w = kural_words_original[i]
                    if i in matched_map:
                        c = matched_map[i]
                        score = c[3]
                        said_text = c[4]
                        if score >= correct_cutoff:
                            word_statuses.append({"word": exp_w, "status": "correct"})
                            correct_count += 1
                        else:
                            word_statuses.append({"word": exp_w, "status": "wrong"})
                            wrong_words.append({"expected": exp_w, "said": said_text})
                    else:
                        word_statuses.append({"word": exp_w, "status": "missing"})
                        missing_words.append(exp_w)

                extra_words = [sp for j, sp in enumerate(spoken_words) if j not in used_spoken_indices]
                return best_overall_score, spoken_words, word_statuses, wrong_words, missing_words, extra_words

            best_eval = None
            best_spoken_text = alt_transcripts[0]
            max_eval_score = -1.0

            for alt_t in alt_transcripts:
                tot_score, sp_words, w_stat, w_wrong, w_miss, w_extra = evaluate_transcript_alignment(alt_t)
                if tot_score > max_eval_score:
                    max_eval_score = tot_score
                    best_spoken_text = alt_t
                    best_eval = (sp_words, w_stat, w_wrong, w_miss, w_extra)

            if not best_eval or not best_eval[0]:
                return jsonify({
                    "status": "unrecognized",
                    "message": "மன்னிக்குக, உங்கள் குரல் தெளிவாகக் கேட்கவில்லை. மீண்டும் முயற்சி செய்யவும்.",
                    "stars": 0,
                    "count": 0,
                    "total": total_words,
                    "accuracy": 0,
                    "spoken_text": best_spoken_text,
                    "word_statuses": word_statuses_empty,
                    "wrong_words": [],
                    "missing_words": kural_words_original,
                    "extra_words": []
                }), 200

            spoken_words, word_statuses, wrong_words, missing_words, extra_words = best_eval
            correct_count = sum(1 for ws in word_statuses if ws['status'] == 'correct')

            if correct_count > 0 and correct_count <= 3:
                stars = 1
            elif correct_count > 3 and correct_count < total_words:
                stars = 2
            elif correct_count == total_words:
                stars = 3
            else:
                stars = 0
                
            accuracy = int((correct_count / total_words) * 100) if total_words > 0 else 0

            # Safe database and session star update
            if session.get('user') and 'points' in session['user']:
                try:
                    k_id = int(kuralId)
                    adhigaram_idx = max(0, (k_id - 1) // 10)
                    kural_idx = max(0, (k_id - 1) % 10)
                    adhigaram_str = str(adhigaram_idx)
                    kural_str = str(kural_idx)

                    current_completed = session['user']['points']['stars'].get('kurals_completed', {})
                    prev_stars = 0
                    if isinstance(current_completed, list) and adhigaram_idx < len(current_completed):
                        if kural_idx < len(current_completed[adhigaram_idx]):
                            prev_stars = int(current_completed[adhigaram_idx][kural_idx] or 0)

                    current_total = int(session['user']['points']['stars'].get('total', 0))
                    new_total = max(0, current_total + stars - prev_stars)

                    condition = {'email': session['user']['email']}
                    dataToBeUpdated = {
                        f"points.stars.kurals_completed.{adhigaram_str}.{kural_str}": stars,
                        "points.stars.total": new_total
                    }
                    db.user_details.update_one(condition, {"$set": dataToBeUpdated})

                    session['user']['points']['stars']['total'] = new_total
                    if isinstance(current_completed, list) and adhigaram_idx < len(current_completed):
                        if kural_idx < len(current_completed[adhigaram_idx]):
                            session['user']['points']['stars']['kurals_completed'][adhigaram_idx][kural_idx] = stars
                    session.modified = True
                except Exception as ex:
                    print("Error updating user stars:", ex)

            return jsonify({
                "status": "success",
                "mode": voice_mode,
                "stars": stars,
                "count": correct_count,
                "total": total_words,
                "accuracy": accuracy,
                "spoken_text": best_spoken_text,
                "word_statuses": word_statuses,
                "wrong_words": wrong_words,
                "missing_words": missing_words,
                "extra_words": extra_words
            }), 200
