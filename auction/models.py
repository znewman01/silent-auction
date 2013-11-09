import datetime
from app import db

class Auction(db.Document):
    start_time = db.DateTimeField(required=True)
    description = db.StringField(max_length=255, required=True)
    auction_id = db.IntegerField(required=True)
    picture_path = db.StringField(required=False)
    bid_range = db.ListField(required=True)
    bidder_public_keys = db.ListField(default=[], required=True)

    def __unicode__(self):
        return self.description