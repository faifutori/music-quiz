import os
import random
import traceback
from flask import Flask, render_template, request, jsonify, url_for, send_from_directory
from pydub import AudioSegment, exceptions as pydub_exceptions

# --- 初期設定 ---
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# --- 定数 ---
MUSIC_DIR = 'music_library'
TEMP_DIR = os.path.join('static', 'temp_audio')

# --- 起動時にフォルダを確認・作成 ---
if not os.path.exists(MUSIC_DIR):
    os.makedirs(MUSIC_DIR)
    print(f"'{MUSIC_DIR}' フォルダを作成しました。")
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)
    print(f"'{TEMP_DIR}' フォルダを作成しました。")

# --- ルート定義 ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/music/<path:filepath>')
def serve_music(filepath):
    """music_libraryから音楽ファイルを直接配信するためのエンドポイント"""
    return send_from_directory(MUSIC_DIR, filepath)

@app.route('/api/groups', methods=['GET'])
def get_groups():
    try:
        groups = [d for d in os.listdir(MUSIC_DIR) if os.path.isdir(os.path.join(MUSIC_DIR, d))]
        return jsonify(groups)
    except Exception:
        return jsonify({"error": f"'{MUSIC_DIR}' フォルダが見つかりません。"}), 500

@app.route('/api/quiz', methods=['POST'])
def get_quiz():
    try:
        data = request.json
        group = data.get('group')
        quiz_type = data.get('quiz_type')
        exclude_list = data.get('exclude_list', [])

        song_paths = []
        base_dir = os.path.join(MUSIC_DIR, group) if group != 'all' else MUSIC_DIR
        
        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith(('.mp3', '.aiff')):
                    song_paths.append(os.path.join(root, file))

        available_songs = [p for p in song_paths if os.path.basename(p) not in exclude_list]

        if not available_songs:
            return jsonify({"error": "全ての曲を出題しました！", "finished": True})

        chosen_song_path = random.choice(available_songs)
        answer = os.path.splitext(os.path.basename(chosen_song_path))[0]
        
        audio_url = ""
        if quiz_type == 'intro':
            relative_path = os.path.relpath(chosen_song_path, MUSIC_DIR)
            audio_url = url_for('serve_music', filepath=relative_path.replace(os.sep, '/'))

        elif quiz_type == 'reverse':
            try:
                # フロントエンドから再生時間を受け取る（デフォルトは15秒）
                duration_s = int(data.get('reverse_duration', 15))
                segment_duration_ms = duration_s * 1000

                song = AudioSegment.from_file(chosen_song_path)
                segment = song[-segment_duration_ms:]
                reversed_segment = segment.reverse()
                
                temp_filename = f"reversed_{os.path.basename(chosen_song_path)}"
                temp_filepath = os.path.join(TEMP_DIR, temp_filename)
                reversed_segment.export(temp_filepath, format="mp3")
                audio_url = url_for('static', filename=f'temp_audio/{temp_filename}')
            except pydub_exceptions.CouldntDecodeError:
                return jsonify({"error": f"音声ファイルの読み込みに失敗: {answer}"}), 500

        return jsonify({
            "answer": answer,
            "audio_url": audio_url,
            "filename": os.path.basename(chosen_song_path)
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"サーバーエラー: {e}"}), 500

if __name__ == '__main__':
    if os.path.exists(TEMP_DIR):
        for file in os.listdir(TEMP_DIR):
            os.remove(os.path.join(TEMP_DIR, file))
    app.run(host='0.0.0.0', port=5001, debug=True)

    # python app.py