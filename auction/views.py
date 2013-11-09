from flask import Blueprint, request, redirect, render_template, url_for
from flask.views import MethodView
from auction.models import Auction

auctions = Blueprint('auctions', __name__, template_folder='templates')

class ListView(MethodView):

    def get(self):
        auctions = Auction.objects.all()
        return render_template('index.html', auctions=auctions)

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
		bidder_number = str(len(auction.bidder_public_keys))
		return render_template('register.html', auction=auction)

class CreateView(MethodView):

	def get(self):
		return render_template('create.html')

	def post(self):
		# request.getargs: description, picture, max and min prices
		# convert max and min into list
		# generate ID
		# add new auction to DB
		return 'Auction # successfully created' # need auction number here
		# should update view to inform of creation


auctions.add_url_rule('/', view_func=ListView.as_view('list'))
auctions.add_url_rule('/auctions/<int:auction_id>/', view_func=DetailView.as_view('detail'))
auctions.add_url_rule('/auctions/<int:auction_id>/register', view_func=RegisterView.as_view('register'))
auctions.add_url_rule('/auctions/create', view_func=CreateView.as_view('create'))
