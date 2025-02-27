from flask import Flask, render_template, request
import os
import subprocess

app = Flask(__name__)

# Direktori untuk menyimpan file video dan sesi tmux
VIDEO_DIR = '/root/videos'
SESSION_DIR = '/root/tmux_sessions'

# Fungsi untuk mendapatkan daftar video
def get_video_files():
    video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith(('.mp4', '.mkv', '.avi'))]
    return video_files

# Fungsi untuk mendapatkan sesi tmux yang aktif
def get_tmux_sessions():
    result = subprocess.run(['tmux', 'ls'], capture_output=True, text=True)
    sessions = result.stdout.strip().splitlines() if result.returncode == 0 else []
    return sessions

@app.route('/')
def index():
    video_files = get_video_files()
    tmux_sessions = get_tmux_sessions()
    return render_template('index.html', video_files=video_files, tmux_sessions=tmux_sessions)

@app.route('/start_stream', methods=['POST'])
def start_stream():
    video_file = request.form['video_file']
    stream_key = request.form['stream_key']
    
    # Perintah untuk menjalankan ffmpeg dalam tmux
    session_name = f"stream_{video_file}"
    command = f"tmux new -d -s {session_name} ffmpeg -stream_loop -1 -re -i {VIDEO_DIR}/{video_file} -f flv -c:v copy -c:a copy rtmp://a.rtmp.youtube.com/live2/{stream_key}"
    
    subprocess.run(command, shell=True)
    return render_template('index.html', message=f"Stream started for {video_file}!")

@app.route('/stop_session', methods=['POST'])
def stop_session():
    session_name = request.form['session_name']
    
    # Perintah untuk menghentikan sesi tmux
    subprocess.run(f"tmux kill-session -t {session_name}", shell=True)
    return render_template('index.html', message=f"Session {session_name} stopped!")

@app.route('/download_video', methods=['POST'])
def download_video():
    file_id = request.form['file_id']
    command = f"gdown https://drive.google.com/uc?id={file_id}"
    subprocess.run(command, shell=True)
    return render_template('index.html', message=f"Video {file_id} downloaded!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
