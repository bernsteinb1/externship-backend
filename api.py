from flask import Flask

app = Flask(__name__)


@app.route('/')
def home():
    return '<h1>Welcome to the API</h1><p>For now, the only endpoint is <a href="/play_cards/">play_cards</a></p>'


@app.route('/play_cards/')
def play_cards():
    # Code for playing cards goes here
    return {'text': 'cards_played'}  # should probably return some form of data for front end


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5105)
