from flask import Flask, send_file, request, render_template
from flask_cors import CORS, cross_origin
from polly import get_tts
import db

app = Flask(__name__)
CORS(app, origins="*")

card_files = {}


@app.route('/')
def home():
    return render_template('API.html')


# Card: { id: number, front: string, back: string }
# CardDeck: { id: number, name: string, content: Card[] }
# DeckList: { id: number, name: string }[]  // a list of card deck info wihout content
@app.route('/create-card/', methods=['POST'])
@cross_origin()
def make_card():
    card = request.get_json()
    card_files[card['id']] = [get_tts(card['front'])]
    card_files[card['id']].append(get_tts(card['back']))
    return 'card-made'


@app.route('/get-card/<card_id>/')
def get_card(card_id):
    idx = 0 if card_id[0] == 'f' else 1
    if idx == 0:
        cid = card_id[5:]
    else:
        cid = card_id[4:]
    return send_file(card_files[cid][idx])


@app.route('/make-user/', methods=['POST'])
def make_user():
    info = request.get_json()
    user_id = info['UserID']
    return db.make_user(user_id)


# This POST request should contain the following info:
# {
#   'UserID': str,
#   'Name': str
# }
@app.route('/make-card-set/', methods=['POST'])
def create_card_set():
    """This will create a card set and assign it an id, which will be returned"""
    info = request.get_json()
    user_id = info['UserID']
    name = info['Name']
    return db.make_card_set(user_id, name)


# This POST request should contain the following info:
# {
#   'UserID': str,
#   'CardSetID': str
# }
@app.route('/delete-card-set/', methods=['POST'])
def delete_card_set():
    info = request.get_json()
    user_id = info['UserID']
    card_set_id = info['CardSetID']
    return db.delete_card_set(user_id, card_set_id)


# This POST request should contain the following info:
# {
#   'UserID': str,
#   'CardSetID': str,
#   'cards': [
#       ['front', 'back'],
#       card2,
#       ...
#   ]
# }
@app.route('/add-cards/', methods=['POST'])
def add_cards():
    info = request.get_json()
    user_id = info['UserID']
    card_set_id = info['CardSetID']
    cards_to_add = info['cards']
    return db.add_items_to_card_set(user_id, card_set_id, cards_to_add)


# This POST request should contain the following info:
# {
#   'UserID': str,
#   'CardSetID': str,
#   'CardIdx': int  // Use zero-indexing on this
# }
@app.route('/delete-card/', methods=['POST'])
def delete_card():
    info = request.get_json()
    user_id = info['UserID']
    card_set_id = info['CardSetID']
    card_idx = info['CardIdx']
    return db.delete_card(user_id, card_set_id, card_idx)


# This POST request should contain the following info:
# {
#   'UserID': str,
#   'CardSetID': str,
#   'CardIdx': int,  // Use zero-indexing on this
#   'NewCard': [
#       'front', 'back'
#   ]
# }
@app.route('/update-card/', methods=['POST'])
def update_card():
    info = request.get_json()
    user_id = info['UserID']
    card_set_id = info['CardSetID']
    card_idx = info['CardIdx']
    new_card = info['NewCard']
    return db.update_card(user_id, card_set_id, card_idx, new_card)


@app.route('/get-owned-sets/<user_id>/')
def get_owned_sets(user_id):
    return db.get_owned_sets(user_id)


@app.route('/get-cards-in-set/<set_id>/')
def get_cards_in_set(set_id):
    return db.get_cards_in_set(set_id)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
