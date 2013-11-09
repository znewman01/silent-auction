from flask import Flask, url_for
from flask.ext.mongoengine import MongoEngine
from mongoengine import connect

app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {'DB': "auctions_db"}
app.config["SECRET_KEY"] = "Q0xfC4nGO7"

db = MongoEngine(app)

@app.route('/')
def hello():
    return 'Hello, world!'

@app.route('/auctions/<int:auction_id>/')
def auction_detail(auction_id):
    return 'Details of auction #%d' % (auction_id)

if __name__ == '__main__':
    app.run()