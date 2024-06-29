from flask import Flask, request, send_from_directory
from pytube import YouTube
from pydub import AudioSegment
import os

app = Flask(__name__)
SONGS_FOLDER = 'songs'

if not os.path.exists(SONGS_FOLDER):
    os.makedirs(SONGS_FOLDER)

@app.route('/api/add-to-queue', methods=['POST'])
def add_to_queue():
    data = request.json
    url = data.get('url')
    channel = data.get('channel')
    if not url or not channel:
        return {'error': 'URL and channel are required'}, 400

    yt = YouTube(url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    audio_file = audio_stream.download()

    audio = AudioSegment.from_file(audio_file, format="mp4")
    wav_file = os.path.join(SONGS_FOLDER, os.path.splitext(os.path.basename(audio_file))[0] + '.wav')
    audio.export(wav_file, format="wav")

    os.remove(audio_file)
    return {'filename': os.path.basename(wav_file)}

@app.route('/songs/<filename>')
def get_song(filename):
    return send_from_directory(SONGS_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
