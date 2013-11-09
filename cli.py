import pickle
import requests
import sys

from auction.crypto import User

def register(server, user, auction_id):
    url = 'http://{}/auctions/{}/register'.format(server, auction_id)
    payload = {'public_key': pickle.dumps(user.export_key())}
    json = requests.post(url, data=payload).json()
    return pickle.loads(json['server_key']), json['bidder_id']

def bid(server, user, auction_id, server_key):
    raw_input('Hit enter when your bidder ID is displayed.')
    bid_url = 'http://{}/auctions/{}/bid'.format(server, auction_id)
    r = requests.get(bid_url)
    json = r.json()
    next_bidder_key = json.get('next_bidder_key', None)
    bid_values = json.get('bid_values')
    print('Available bid values: {}'.format(bid_values))
    bid = int(raw_input('What is your bid? '))
    blob = pickle.loads(json['blob'])
    print(blob)
    print('---')
    if next_bidder_key is not None:
        blob = user.bid(blob, bid, bid_values, server_key, pickle.loads(next_bidder_key))
    else:
        blob = user.final_bid(blob, bid, bid_values, server_key)
    print(blob)
    print(requests.post(bid_url, data={'blob': pickle.dumps(blob)}).text)



def main():
    user = User()
    user.gen_key(128)

    server = 'localhost:5000'
    if len(sys.argv) == 2:
        server = sys.argv[1]

    auction_id = raw_input('What auction id? ')

    server_key, bidder_id = register(server, user, auction_id)

    print('Your bidder ID: ', bidder_id)

    bid(server, user, auction_id, server_key)

if __name__ == '__main__':
    main()
