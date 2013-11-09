import datetime
from auction import db
from flask import g
from crypto import Server

class Auction(db.Document):
    start_time = db.DateTimeField(required=True)
    description = db.StringField(max_length=255, required=True)
    auction_id = db.IntField(required=True)
    picture_path = db.StringField(required=False)
    bid_range = db.ListField(required=True)
    bidder_public_keys = db.ListField(default=[], required=False)

    def __unicode__(self):
        return self.description

def get_crypto_server():
    server = getattr(g, 'server', None)
    if server is None:
        server = g.server = Server(1)
        server.gen_key(64)
    return server
