import pickle
import requests
import sys
import argparse

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
    seller_address = json['seller_address']
    print('Available bid values: {}'.format(bid_values))
    bid = int(raw_input('What is your bid? '))
    blob = pickle.loads(json['blob'])
    if next_bidder_key is not None:
        blob = user.bid(blob, bid, bid_values, server_key,
                pickle.loads(next_bidder_key), seller_address)
    else:
        blob = user.final_bid(blob, bid, bid_values, server_key, seller_address)
    print(requests.post(bid_url, data={'blob': pickle.dumps(blob)}).text)



def main():
    parser = argparse.ArgumentParser(description='Place a SilentAuction bid')
    parser.add_argument('--server', default='localhost:5000')
    parser.add_argument('--keyfile', default=None)
    args = parser.parse_args()

    user = User(key=pickle.load(open(args.keyfile)))
    if not args.keyfile:
        user.gen_key(4096)

    auction_id = raw_input('What auction id? ')

    server_key, bidder_id = register(args.server, user, auction_id)

    print('Your bidder ID: {}'.format(bidder_id))

    bid(args.server, user, auction_id, server_key)

if __name__ == '__main__':
    main()
