from flask import Flask, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins="*")

sound_files = ['output.mp3', 'clock.mp3', 'geese.mp3', 'laser.mp3', 'orchestra.mp3']

@app.route('/')
def home():
    return '<h1>Welcome to the API</h1><p>For now, the only endpoint is <a href="/play_cards/">play_cards</a></p>'


@app.route('/play_cards/<int:sound_id>/')
def play_cards(sound_id):
    # Code for playing cards goes here
    return send_file(sound_files[sound_id], download_name='output.mp3')  # should probably return some form of data for front end


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
