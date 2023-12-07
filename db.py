from boto3 import Session
import uuid


def make_user(user_id):
    db_conn = Session().client('dynamodb')
    db_conn.put_item(
        TableName='Users',
        Item={
            'UserID': {
                'S': f'{user_id}'
            }
        }
    )
    return f"Created User {user_id}"


def make_card_set(user_id, card_set_name):
    db_conn = Session().client('dynamodb')
    try:
        user_card_sets = db_conn.get_item(
            TableName='Users',
            Key={
                'UserID': {
                    'S': user_id
                }
            }
        )
        item = user_card_sets['Item']
    except:
        return "Something went wrong with retrieving user"

    set_id_not_unique = True
    while set_id_not_unique:
        card_set_id = str(uuid.uuid4())
        if 'Item' not in db_conn.get_item(
            TableName='CardSets',
            Key={
                'CardSetID': {
                    'S': card_set_id
                }
            }
        ):
            set_id_not_unique = False

    if 'CardSets' in item:
        user_sets = user_card_sets['Item']['CardSets']['SS'] + [card_set_id]
    else:
        user_sets = [card_set_id]
    db_conn.put_item(
        TableName='Users',
        Item={
            'UserID': {
                'S': f'{user_id}'
            },
            'CardSets': {
                'SS': user_sets
            }
        }
    )
    db_conn.put_item(
        TableName='CardSets',
        Item={
            'CardSetID': {
                'S': card_set_id
            },
            'Name': {
                'S': card_set_name
            }
        }
    )
    return card_set_id


def delete_card_set(user_id, card_set_id):
    if not verify_set_ownership(user_id, card_set_id):
        return "You do not own this set!"
    db_conn = Session().client('dynamodb')
    db_conn.delete_item(
        TableName='CardSets',
        Key={
            'CardSetID': {
                'S': str(card_set_id)
            }
        }
    )

    new_user_deck_list = db_conn.get_item(
        TableName='Users',
        Key={
            'UserID': {
                'S': user_id
            }
        }
    )['Item']['CardSets']['SS']
    new_user_deck_list.remove(str(card_set_id))
    if len(new_user_deck_list) > 0:
        db_conn.put_item(
            TableName='Users',
            Item={
                'UserID': {
                    'S': user_id
                },
                'CardSets': {
                    'SS': new_user_deck_list
                }
            }
        )
    else:
        db_conn.put_item(
            TableName='Users',
            Item={
                'UserID': {
                    'S': user_id
                },
            }
        )
    return f'Set {card_set_id} deleted'


def add_items_to_card_set(user_id, card_set_id, cards):
    if not verify_set_ownership(user_id, card_set_id):
        return "You do not own this set!"
    db_conn = Session().client('dynamodb')
    current_set = db_conn.get_item(
        TableName='CardSets',
        Key={
            'CardSetID': {
                'S': str(card_set_id)
            }
        }
    )

    if 'Item' not in current_set:
        return 'Query Failed'
    current_set_name = current_set['Item']['Name']['S']
    if 'CardFronts' not in current_set['Item']:
        card_fronts = []
        card_backs = []
    else:
        card_fronts = current_set['Item']['CardFronts']['L']
        card_backs = current_set['Item']['CardBacks']['L']

    for card in cards:
        card_fronts.append({'S': card[0]})
        card_backs.append({'S': card[1]})

    db_conn.put_item(
        TableName='CardSets',
        Item={
            'CardSetID': {
                'S': str(card_set_id),
            },
            'CardFronts': {
                'L': card_fronts
            },
            'CardBacks': {
                'L': card_backs
            },
            'Name': {
                'S': current_set_name
            }
        }
    )
    return f"Added cards {str(cards)} to the set"


def delete_card(user_id, card_set_id, card_idx):
    if not verify_set_ownership(user_id, card_set_id):
        return "You do not own this set!"
    db_conn = Session().client('dynamodb')
    card_set = db_conn.get_item(
        TableName='CardSets',
        Key={
            'CardSetID': {
                'S': card_set_id
            }
        }
    )
    if 'Item' not in card_set:
        return f'Card set {card_set_id} does not exist!'
    del card_set['Item']['CardFronts']['L'][card_idx]
    del card_set['Item']['CardBacks']['L'][card_idx]
    db_conn.put_item(
        TableName='CardSets',
        Item={
            'CardSetID': {
                'S': card_set_id
            },
            'Name': card_set['Item']['Name'],
            'CardFronts': card_set['Item']['CardFronts'],
            'CardBacks': card_set['Item']['CardBacks']
        }
    )
    return f'Card at index {card_idx} deleted.'


def update_card(user_id, card_set_id, card_idx, new_card):
    if not verify_set_ownership(user_id, card_set_id):
        return "You do not own this card set!"
    db_conn = Session().client('dynamodb')
    cards = db_conn.get_item(
        TableName='CardSets',
        Key={
            'CardSetID': {
                'S': str(card_set_id)
            }
        }
    )['Item']
    cards['CardFronts']['L'][card_idx]['S'] = new_card[0]
    cards['CardBacks']['L'][card_idx]['S'] = new_card[1]
    db_conn.put_item(
        TableName='CardSets',
        Item={
            'CardSetID': {
                'S': str(card_set_id),
            },
            'Name': cards['Name'],
            'CardFronts': cards['CardFronts'],
            'CardBacks': cards['CardBacks']
        }
    )
    return f'Card {card_idx} updated!'


def verify_set_ownership(user_id: str, list_id: str) -> bool:
    db_conn = Session().client('dynamodb')
    try:
        user_card_sets = db_conn.get_item(
            TableName='Users',
            Key={
                'UserID': {
                    'S': user_id
                }
            }
        )
        user_card_sets = user_card_sets['Item']['CardSets']['SS']
    except:
        return False
    return list_id in user_card_sets


def get_owned_sets(user_id):
    db_conn = Session().client('dynamodb')
    user_info = db_conn.get_item(
        TableName='Users',
        Key={
            'UserID': {
                'S': user_id
            }
        }
    )
    if 'Item' not in user_info:
        return 'User not found.'
    if 'CardSets' not in user_info['Item']:
        return {}
    ret = {}
    sets = user_info['Item']['CardSets']['SS']
    for set in sets:
        set_info = db_conn.get_item(
            TableName='CardSets',
            Key={
                'CardSetID': {
                    'S': set
                }
            }
        )
        if 'Item' not in set_info:
            continue
        ret[set] = set_info['Item']['Name']['S']
    return ret


def get_cards_in_set(set_id):
    db_conn = Session().client('dynamodb')
    set_info = db_conn.get_item(
        TableName='CardSets',
        Key={
            'CardSetID': {
                'S': set_id
            }
        }
    )
    if 'Item' not in set_info:
        return 'Set ID not in DB'
    ret = {'set': []}
    if 'CardFronts' not in set_info['Item']:
        return ret
    for i in range(len(set_info['Item']['CardFronts']['L'])):
        ret['set'].append([
            set_info['Item']['CardFronts']['L'][i]['S'],
            set_info['Item']['CardBacks']['L'][i]['S']
        ])
    return ret


if __name__ == '__main__':
    # print(make_user('1'))
    # gerald_id = make_card_set('1', 'Gerald')
    # print(add_items_to_card_set('1', gerald_id, [['hello', 'hola'], ['goodbye', 'adios']]))
    # print(add_items_to_card_set('1', gerald_id, [['What is your name?', 'Como Te Llamas']]))
    # print(make_user('2'))
    # print(update_card(gerald_id, 0, '2', ['haha', 'lol']))
    # print(update_card(gerald_id, 1, '1', ['I will delete this', 'Be destroyed.']))
    # wayne_id = make_card_set('1', 'Wayne')
    # print(delete_card_set('1', wayne_id))
    print(delete_card('1', '39b032b7-a537-4416-9a32-6e402417982d', 1))
