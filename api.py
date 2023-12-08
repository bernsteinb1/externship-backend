from flask import Flask, send_file, request, render_template, redirect
from flask_cors import CORS, cross_origin
from polly import get_tts_s3
from werkzeug.middleware.proxy_fix import ProxyFix
import db

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config['PREFERRED_URL_SCHEME'] = 'https'
CORS(app, origins="*")


@app.route('/')
def home():
    return render_template('API.html')


@app.route('/create-card/', methods=['POST'])
def create_card():
    req = request.get_json()
    get_tts_s3(req['front'])
    get_tts_s3(req['back'])
    return 'TTS generated'


@app.route('/get-card/<text>/')
def get_card(text):
    return redirect(get_tts_s3(text))


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
#   'CardSetID': str,
#   'NewName': str
# }
@app.route('/rename-card-set/', methods=['POST'])
def rename_card_set():
    info = request.get_json()
    user_id = info['UserID']
    card_set_id = info['CardSetID']
    new_name = info['NewName']
    return db.rename_card_set(user_id, card_set_id, new_name)



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
