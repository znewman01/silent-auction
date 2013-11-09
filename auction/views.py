import json
import os
import pickle
import random

from flask import Blueprint, request, redirect, render_template, url_for, send_from_directory
from flask.views import MethodView
from auction import app
from auction.models import Auction, get_upload_folder
from werkzeug import secure_filename

auctions = Blueprint('auctions', __name__, template_folder='templates')

class ImageView(MethodView):

    def get(self, filename):
        return send_from_directory(get_upload_folder(), filename) # TODO(zjn): attone for my sins

class ListView(MethodView):

    def get(self):
        auctions = Auction.objects.all()
        return render_template('index.html', auctions=auctions, picture_directory=get_upload_folder())

class DetailView(MethodView):

    def get(self, auction_id):
        auction = Auction.objects.get_or_404(auction_id=auction_id)
        return render_template('detail.html', auction=auction)

class RegisterView(MethodView):

    def post(self, auction_id):
        key = request.form['public_key']
        auction = Auction.objects(auction_id=auction_id).first()
        auction.bidder_public_keys.append(key)
        auction.save()
        bidder_id = len(auction.bidder_public_keys)
        server = auction.get_crypto_server()
        server_key = pickle.dumps(server.export_key())
        payload = {
                'server_key': server_key,
                'bidder_id': bidder_id
            }
        return json.dumps(payload)

class BidView(MethodView):

    def get(self, auction_id):
        auction = Auction.objects(auction_id=auction_id).first()
        server = auction.get_crypto_server()
        next_bidder_key = None
        if auction.current_state is None:
            auction.current_bid = 1
            first_bidder_key = \
                    auction.bidder_public_keys[0]
            blob = server.initialize(pickle.loads(first_bidder_key))
            auction.current_state = pickle.dumps(server.initialize(pickle.loads(first_bidder_key)))

        if auction.current_bid < len(auction.bidder_public_keys):
            next_bidder_key = auction.bidder_public_keys[auction.current_bid]

        payload = {
                'blob': auction.current_state,
                'bid_values': auction.bid_range,
                'seller_address': auction.account
            }

        auction.save()
        if next_bidder_key is not None:
            payload['next_bidder_key'] = next_bidder_key
        return json.dumps(payload)

    def post(self, auction_id):
        auction = Auction.objects(auction_id=auction_id).first()
        blob = request.form['blob']
        auction.current_state = blob
        auction.current_bid += 1
        auction.save()
        if auction.current_bid > len(auction.bidder_public_keys):
            server = auction.get_crypto_server()
            blob = server.finalize(pickle.loads(blob))
            auction.current_state = pickle.dumps(blob)
            return str(blob)
        return ''

class CreateView(MethodView):

    def get(self):
        return render_template('create.html')

    def post(self):
        bid_range = list(range(int(request.form['startingBid']), int(request.form['maxBid']) + 1))
        file = request.files['image']
        filename = None
        if file:
            filename = secure_filename(file.filename)
            full_path = os.path.join(get_upload_folder(), filename)
            file.save(full_path)
        while True:
            auction_id = random.randint(1,10**5)
            if not Auction.objects(auction_id=auction_id):
                break
        auction = Auction(name=request.form['name'],
                account=request.form['account'],
                description=request.form['description'], auction_id=auction_id,
                bid_range=bid_range, picture_filename=filename)
        auction.save()
        return render_template('create.html', message = 'Auction #{} successfully created'.format(auction_id))

auctions.add_url_rule('/', view_func=ListView.as_view('list'))
auctions.add_url_rule('/user_images/<filename>', view_func=ImageView.as_view('image')) 
auctions.add_url_rule('/auctions/<int:auction_id>/', view_func=DetailView.as_view('detail'))
auctions.add_url_rule('/auctions/<int:auction_id>/register', view_func=RegisterView.as_view('register'))
auctions.add_url_rule('/auctions/<int:auction_id>/bid', view_func=BidView.as_view('bid'))
auctions.add_url_rule('/auctions/create', view_func=CreateView.as_view('create'))
