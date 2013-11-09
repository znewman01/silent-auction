import datetime
import pickle
from auction import db, app
from flask import g
from crypto import Server

class Auction(db.Document):
    name = db.StringField(max_length=63, required=True)
    description = db.StringField(required=True)
    account = db.StringField(required=True)
    auction_id = db.IntField(required=True)
    picture_filename = db.StringField(required=False)
    bid_range = db.ListField(required=True)

    auctioneer = db.StringField(required=False)
    current_state = db.StringField(required=False)
    current_bid = db.IntField(required=False)
    bidder_public_keys = db.ListField(default=[], required=False)

    def __unicode__(self):
        return self.description

    def get_crypto_server(self):
        server = self.auctioneer
        if server is None:
            server = Server(len(self.bid_range), 4)
            server.gen_key(2048)
            self.auctioneer = pickle.dumps(server)
            self.save()
        else:
            server = pickle.loads(server)
        return server

def get_upload_folder():
    return app.config["UPLOAD_FOLDER"]
