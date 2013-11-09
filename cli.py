import pickle
import requests
import sys
import argparse
import binascii
import decimal
import io

from pycoin import encoding
from pycoin.convention import tx_fee, btc_to_satoshi, satoshi_to_btc
from pycoin.services import blockchain_info
from pycoin.tx import Tx, UnsignedTx, TxOut, SecretExponentSolver


from auction.crypto import User

def register(server, user, auction_id):
    url = 'http://{}/auctions/{}/register'.format(server, auction_id)
    payload = {'public_key': pickle.dumps(user.export_key())}
    json = requests.post(url, data=payload).json()
    return pickle.loads(json['server_key']), json['bidder_id']

def bitcoin(public, private, address, amount):
     coins_from = []
     coins_sources = blockchain_info.coin_sources_for_address(public)
     coins_from.extend(coins_sources)
     value = sum(cs[-1].coin_value for cs in coins_sources)

     secret_exponents = [encoding.wif_to_secret_exponent(private)]

     amount = btc_to_satoshi(amount)
     coins_to = []
     coins_to.append((amount, address))
     actual_tx_fee = value - amount
     if actual_tx_fee < 0:
         print("not enough source coins (%s BTC) for destination (%s BTC). Short %s BTC" %   (satoshi_to_btc(total_value), satoshi_to_btc(total_spent), satoshi_to_btc(-actual_tx_fee)))
         return None;

     if actual_tx_fee > 0:
        coins_to.append((actual_tx_fee, public))

     unsigned_tx = UnsignedTx.standard_tx(coins_from, coins_to)
     solver = SecretExponentSolver(secret_exponents)
     new_tx = unsigned_tx.sign(solver)
     s = io.BytesIO()
     new_tx.stream(s)
     tx_bytes = s.getvalue()
     tx_hex = binascii.hexlify(tx_bytes).decode("utf8")

     return tx_bytes

def bid(server, user, auction_id, server_key, btc_public, btc_private):
    raw_input('Hit enter when your bidder ID is displayed.')
    bid_url = 'http://{}/auctions/{}/bid'.format(server, auction_id)
    r = requests.get(bid_url)
    json = r.json()
    next_bidder_key = json.get('next_bidder_key', None)
    bid_values = json.get('bid_values')
    seller_address = json['seller_address']
    print('Available bid values: {}'.format(bid_values))
    bid = int(raw_input('What is your bid? '))

    btc = bitcoin(btc_public, btc_private, seller_address, bid/1000);
    if btc is None:
        return

    blob = pickle.loads(json['blob'])
    if next_bidder_key is not None:
        blob = user.bid(blob, bid, bid_values, server_key,
                pickle.loads(next_bidder_key), btc)
    else:
        blob = user.final_bid(blob, bid, bid_values, server_key, btc)
    print(requests.post(bid_url, data={'blob': pickle.dumps(blob)}).text)

def main():
    parser = argparse.ArgumentParser(description='Place a SilentAuction bid')
    parser.add_argument('--server', default='localhost:5000')
    parser.add_argument('--keyfile', default=None)
    args = parser.parse_args()

    user = User(key=pickle.load(open(args.keyfile)))
    if not args.keyfile:
        user.gen_key(4096)
    bitcoin_address = raw_input('What Bitcoin address?')
    bitcoin_wif = raw_input('What Bitcoin wif?');

    server = 'localhost:5000'
    if len(sys.argv) == 2:
        server = sys.argv[1]

    auction_id = raw_input('What auction id? ')

    server_key, bidder_id = register(args.server, user, auction_id)

    print('Your bidder ID: {}'.format(bidder_id))

    bid(args.server, user, auction_id, server_key, bitcoin_address, bitcoin_wif)

if __name__ == '__main__':
    main()
