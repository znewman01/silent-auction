from flask import Flask
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__)
app.config["MONGODB_SETTINGS"] = {'DB': "auctions_db"}
app.config["SECRET_KEY"] = "Q0xfC4nGO7"
app.config["UPLOAD_FOLDER"] = '/tmp/img_uploads'

db = MongoEngine(app)


def register_blueprints(app):
    # Prevents circular imports
    from auction.views import auctions
    app.register_blueprint(auctions)

register_blueprints(app)

if __name__ == '__main__':
    app.debug = True
    app.run()
