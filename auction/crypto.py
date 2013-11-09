import datetime
import tempfile

from Crypto import Random
from Crypto.PublicKey import ElGamal
from Crypto.Random import random
from Crypto.Util.number import GCD


def encrypt(plaintext, key):
    while 1:
        k = random.StrongRandom().randint(1,key.p-1)
        if GCD(k,key.p-1)==1: break
    return key.encrypt(plaintext, k)

def encrypt_cipher(ciphertext, key):
    return (encrypt(ciphertext[0], key),
            encrypt(ciphertext[1], key))

def decrypt(ciphertext, key):
        return key.decrypt(ciphertext)

def scale(ciphertext, scalar):
    return ciphertext[0], scalar * ciphertext[1]


class User():

    def __init__(self, key=None):
        self.key = key

    def gen_key(self, key_len=4096):
        self.key = ElGamal.generate(key_len, Random.new().read)

    def export_key(self):
        return self.key.publickey()

    def bid(self, blob, value, bid_list, server_key, next_bidder_key):
        def make_garbage(chunks):
            for chunk in chunks:
                garbage = random.StrongRandom().randint(1, server_key.p-1)
                encrypted = encrypt(garbage, server_key)
                yield encrypt_cipher(encrypted, next_bidder_key)
        def place_bid(chunks, value):
            for chunk in chunks:
                yield encrypt_cipher(scale(chunk, 0xBEEF), next_bidder_key)
        def pass_through(chunks):
            for chunk in chunks:
                yield encrypt_cipher(chunk, next_bidder_key)

        ret = []
        for i, bid_blob in enumerate(blob):
            chunks = []
            for chunk in bid_blob:
                chunks.append((decrypt(chunk[0], self.key), decrypt(chunk[1], self.key)))
            if bid_list[i] < value:
                chunks = list(make_garbage(chunks))
            elif bid_list[i] == value:
                chunks = list(place_bid(chunks, value))
            else:
                chunks = list(pass_through(chunks))
            ret.append(chunks)
        return ret

    def final_bid(self, blob, value, bid_list, server_key):
        def make_garbage(chunks):
            for chunk in chunks:
                garbage = random.StrongRandom().randint(1, server_key.p-1)
                yield encrypt(garbage, server_key)
        def place_bid(chunks, value):
            for chunk in chunks:
                yield scale(chunk, 0xBEEF)
        def pass_through(chunks):
            for chunk in chunks:
                yield chunk

        ret = []
        for i, bid_blob in enumerate(blob):
            chunks = []
            for chunk in bid_blob:
                chunks.append((decrypt(chunk[0], self.key), decrypt(chunk[1], self.key)))
            if bid_list[i] < value:
                chunks = list(make_garbage(chunks))
            elif bid_list[i] == value:
                chunks = list(place_bid(chunks, value))
            else:
                chunks = list(pass_through(chunks))
            ret.append(chunks)
        return ret



class Server():

    def __init__(self, num_bids, blocks_per_bid=4):
        self.num_bids = num_bids
        self.blocks_per_bid = blocks_per_bid

    def gen_key(self, key_len=2048):
        self.key = ElGamal.generate(key_len, Random.new().read)

    def export_key(self):
        return self.key.publickey()

    def initialize(self, first_bidder_key):
        blob = []
        for _ in range(self.num_bids):
            bid_blob = []
            for _ in range(self.blocks_per_bid):
                value = 1
                encrypted = encrypt(value, self.key)
                double_encrypted = encrypt_cipher(encrypted, first_bidder_key)
                bid_blob.append(double_encrypted)
            blob.append(bid_blob)
        return blob

    def finalize(self, blob):
        ret = []
        for bid_blob in blob:
            chunks = []
            for chunk in bid_blob:
                chunks.append(decrypt(chunk, self.key))
            ret.append(chunks)
        return ret


def main():
    # do a test auction
    num_users = 3
    num_bids = 10
    users = [User() for _ in range(num_users)]
    server_key_len = 64
    for user in users:
        user.gen_key(server_key_len * 2)
    server = Server(num_bids, 1)
    server.gen_key(server_key_len)
    server_key = server.export_key()
    keyring = [user.export_key() for user in users]

    blob = server.initialize(keyring[0])

    blob = users[0].bid(blob, 5, range(num_bids), server_key, keyring[1])
    blob = users[1].bid(blob, 3, range(num_bids), server_key, keyring[2])
    blob = users[2].final_bid(blob, 8, range(num_bids), server_key)
    blob = server.finalize(blob)
    print(blob)


if __name__ == '__main__':
    main()
