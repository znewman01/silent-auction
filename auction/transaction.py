import binascii
import requests

from pycoin import encoding
from pycoin.tx import Tx, UnsignedTx, TxOut, SecretExponentSolver

def submit_tx(tx_bytes):
    tx_hex = binascii.hexlify(tx_bytes).decode("utf8")
    args = {'tx': tx_bytes}
    r = requests.post("https://blockchain.info/pushtx", data=args)
    if r.status_code == 200:
        return True
    else:
        return False

