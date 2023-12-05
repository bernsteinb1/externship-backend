from flask import Flask, send_file, request
from flask_cors import CORS, cross_origin
from polly import get_tts

app = Flask(__name__)
CORS(app, origins="*")

card_files = {}


@app.route('/')
def home():
    return ('<h1>Welcome to the API</h1>'
            '<p>For now, the only endpoints are <a href="/create-card/">create-card</a> and <a href="/get-card/">get-card</a></p>'
            '<p>create-card expects a POST request containing a jsonified card object, get-card expects a url with "front<card_id> or back<card_id>"')


# Card: { id: number, front: string, back: string }
# CardDeck: { id: number, name: string, content: Card[] }
# DeckList: { id: number, name: string }[]  // a list of card deck info wihout content
@app.route('/create-card/', methods = ['POST'])
@cross_origin()
def make_card():
    card = request.get_json()
    card_files[card['id']] = [get_tts(card['front'])]
    card_files[card['id']].append(get_tts(card['back']))
    return 'card-made'


@app.route('/get-card/<card_id>/')
@cross_origin()
def get_card(card_id):
    idx = 0 if card_id[0] == 'f' else 1
    if idx == 0:
        cid = card_id[5:]
    else:
        cid = card_id[4:]
    return send_file(card_files[cid][idx])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
