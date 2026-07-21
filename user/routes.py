from flask import Flask, sessions, render_template
from user.audioProcessing import AudioProceesing
from user.kural import kural
from app import app, login_required,session
from user.models import User


@app.route('/user/signup', methods=['POST'])
def signup():
    return User().signup()


@app.route('/user/signout')
def signout():
    return User().signout()


@app.route('/user/login', methods=['POST'])
def login():
    return User().login()


@app.route('/practice_thirukkural',  methods=["POST"])
def practice():
    return AudioProceesing().practice()


@app.route('/filter_adhigaram',  methods=["POST"])
def fetchKural():
    return kural().fetchKural()

@app.route('/selected_game', methods=['POST'])
def selected_game():
    return kural().selected_game()

from app import login_required
@app.route('/learn_thirukkural', methods=["GET"])
@login_required
def learn_thirukkural():
    return kural().learn_thirukkural()



@app.route('/drag_drop_game', methods=["GET"])
def drag_drop_game():
    return kural().drag_drop_game()


@app.route('/evaluate_drag_game',  methods=["POST"])
def evaluate_drag_game():
    return kural().evaluate_drag_game()



@app.route('/fillups_game', methods=["GET"])
def fillups_game():
    return kural().fillups_game()

@app.route('/evaluate_fillups_game',  methods=["POST"])
def evaluate_fillups_game():
    return kural().evaluate_fillups_game()


@app.route("/transaltee", methods=['POST', 'GET'])
def transaltee():
    return AudioProceesing().compareKural()


# N-gram Prediction Game Routes
@app.route('/ngram/game', methods=['GET'])
@login_required
def ngram_game():
    return kural().ngram_game()


@app.route('/ngram/get_kural', methods=['GET'])
@login_required
def get_ngram_kural():
    return kural().get_ngram_kural()


@app.route('/ngram/predict', methods=['POST'])
@login_required
def ngram_predict():
    return kural().ngram_predict()


@app.route('/ngram/submit_score', methods=['POST'])
@login_required
def submit_ngram_score():
    return kural().submit_ngram_score()


@app.route('/ngram/leaderboard', methods=['GET'])
@login_required
def ngram_leaderboard():
    return kural().ngram_leaderboard()

@app.route('/get_kural_action/<int:kural_id>', methods=['GET'])
@login_required
def get_kural_action(kural_id):
    from flask import jsonify
    # Using a standard public domain placeholder video since we don't have real videos yet
    video_url = "https://www.w3schools.com/html/mov_bbb.mp4" 
    return jsonify({"success": True, "video_url": video_url})


@app.route('/get_kural_audio/<int:kural_id>', methods=['GET'])
@login_required
def get_kural_audio(kural_id):
    import os
    import asyncio
    from flask import jsonify, url_for
    from tts import text_to_speech
    from app import db

    # 1. Determine paths
    static_audio_dir = os.path.join(app.static_folder, 'audio')
    os.makedirs(static_audio_dir, exist_ok=True)

    # 2. Check for pre-existing .wav file (backwards compatibility)
    wav_filename = f"kural{kural_id}.wav"
    wav_filepath = os.path.join(static_audio_dir, wav_filename)
    if os.path.exists(wav_filepath):
        audio_url = url_for('static', filename=f'audio/{wav_filename}')
        return jsonify({"audio_url": audio_url}), 200

    # 3. Check for pre-existing generated .mp3 file
    mp3_filename = f"kural{kural_id}.mp3"
    mp3_filepath = os.path.join(static_audio_dir, mp3_filename)
    if os.path.exists(mp3_filepath):
        audio_url = url_for('static', filename=f'audio/{mp3_filename}')
        return jsonify({"audio_url": audio_url}), 200

    # 4. Generate TTS if not found
    try:
        kural_data = db['kural_data']
        query = {"kural_id": kural_id}
        kural_record = kural_data.find_one(query)
        if not kural_record:
            return jsonify({"error": "குறள் கண்டறியப்படவில்லை"}), 404

        line1 = kural_record['kural'][0][0]
        line2 = kural_record['kural'][1][0]
        full_text = f"{line1}\n{line2}"

        # Run async edge-tts in a dedicated event loop for this request thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(text_to_speech(
                text=full_text,
                voice='ta-IN-ValluvarNeural',
                rate='-12%',
                output_filename=mp3_filepath
            ))
        finally:
            loop.close()

    except Exception as e:
        return jsonify({"error": f"TTS API Exception: {str(e)}"}), 500

    audio_url = url_for('static', filename=f'audio/{mp3_filename}')
    return jsonify({"audio_url": audio_url}), 200