from flask import Flask, send_file
from flask_cors import CORS, cross_origin
from polly import get_tts

app = Flask(__name__)
CORS(app, origins="*")


@app.route('/')
def home():
    return '<h1>Welcome to the API</h1><p>For now, the only endpoint is <a href="/play_cards/">play_cards</a></p>'


@app.route('/play_cards/<text>/')
@cross_origin()
def play_cards(text):
    # Code for playing cards goes here
    return send_file(get_tts(text), download_name='output.mp3')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
