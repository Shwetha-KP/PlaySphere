from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.db.utils import OperationalError
from django.utils.datastructures import MultiValueDictKeyError
from hashlib import md5
import json
import razorpay
from store.models import Game, BoughtGames
from django.contrib.auth.models import User
from .models import HighScore
from .models import GameState
from .models import ratings
import os
import telepot

# Renders the main view
def index(request, game_id):
	# Checks what game is being currently viewed from the id
	try:
		current_game = Game.objects.get(id=game_id)
	except Game.DoesNotExist:
		raise Http404("Game does not exist")

	# Gets users id
	user_id = request.user.id

	# Retrieves global top five scores associated with this game
	high_score_list = HighScore.objects.all().filter(game=current_game).order_by('-score')[:5]

	# Checks if user owns or has developed this game, True if does, False if not
	if request.user.is_authenticated():
		user_owns_game = len(BoughtGames.objects.all().filter(game=current_game).filter(user=request.user)) > 0
		user_developed_game = len(Game.objects.all().filter(name=current_game.name).filter(developer_id=user_id)) > 0
	else:
		user_owns_game = False
		user_developed_game = False
	
	gamename = Game.objects.all().filter(id=game_id).values()[0]['name']
	print("------------------")
	mydata = ratings.objects.all().filter(game=gamename)
	print(mydata)
	print("------------------")

	context = {'object_list':mydata, 'game': current_game, 'high_scores': high_score_list, 'owned': user_owns_game, 'developed': user_developed_game, 'logged_in': request.user.is_authenticated(), 'game_id': game_id}
	return render(request, 'gameview/index.html', context)

# Defines an 'endpoint' for our ajax POST function in the gameview template.
# When submitting a score, a function sends the score with an ajax function
# and it gets handled here.
def score(request, game_id):
	post = request.POST
	# Accessed via the key value
	try:
		score = post['score']
	# In case of invalid data being sent to the endpoint
	except MultiValueDictKeyError:
		return HttpResponse(status=400)
	# gets the correct game being played
	currentGame = Game.objects.get(id=game_id)
	# adds a new high score model/object
	newScore = HighScore(player=request.user, score=score, game=currentGame)
	newScore.save()

	return HttpResponse(status=201)

# This endpoint retrieves the top 5 high scores for the game
def scores(request, game_id):
	# Gets current game or returns 404 if not found
	currentGame = get_object_or_404(Game, id=game_id)

	# Retrieves all scores, filters out top five associated with the current game
	scores = HighScore.objects.all().filter(game=currentGame).order_by('-score')[:5]

	# Loop through scores, generate data
	data = [{'score': item.score, 'player': item.player.username } for item in scores]

	# Return as json
	return HttpResponse(json.dumps(data), content_type='application/json')

# Endpoint receives game state and saves it to the database
def state(request, game_id):
	# Get post content
	post = request.POST

	# Access state from HTTP post
	try:
		state = post['state']
	except MultiValueDictKeyError:
		return HttpResponse(status=400)

	# Get game or 404
	currentGame = get_object_or_404(Game, id=game_id)

	# Creates new state in the database
	newState = GameState(player=request.user, state=state, game=currentGame)
	newState.save()

	# Returns 'created' response code
	return HttpResponse(status=201)

# Endpoint returns most recently saved game
def load(request, game_id):
	# Gets current game
	currentGame = get_object_or_404(Game, id=game_id)

	try:
		mostRecentSave = GameState.objects.all().filter(game=currentGame).filter(player=request.user).order_by('-date')[:1]
	# If try give operationalError, meaning no saves found
	except OperationalError:
		return (HttpResponse(status=400))
	# Check if most recent save is empty or not
	if not mostRecentSave:
		return (HttpResponse(status=400))

	else:
		data = [{'data': item.state} for item in mostRecentSave]
		return HttpResponse(json.dumps(data), content_type='application/json')

# Handles game purchases
@login_required
def buy_game(request, game_id):
	game = Game.objects.get(id=game_id)
	user_id = request.user.id

	# Check if user owns this game
	user_owns_game = len(BoughtGames.objects.all().filter(game=game).filter(user=request.user)) > 0
	# Check if user has developed this game
	user_developed_game = len(Game.objects.all().filter(name=game.name).filter(developer_id=user_id)) > 0

	if request.user.is_authenticated() and not user_owns_game and not user_developed_game:
		pid = str(user_id) + "-" + game_id # Can be any random id, just needs to be unique
		sid = "AKAGameStore"
		amount = game.price
		secret_key = "5ba99a03e46a687041b16ec552bcdf9c"
		checksum_str = "pid={}&sid={}&amount={}&token={}".format(pid, sid, amount, secret_key)
		m = md5(checksum_str.encode("ascii")) # encoding the checksum
		checksum = m.hexdigest()
		current_host = request.META.get('HTTP_HOST')
		print('payament {}'.format(amount))
		client = razorpay.Client(auth =("rzp_test_ifqXZb84qSL1CP" , "IwSyyaBvXh300nlqM0kqb0ow"))
		payment = client.order.create({'amount':amount, 'currency':'EUR','payment_capture':'1' })
		Id = payment['id']
		context = {
			'pid': pid,
			'sid': sid,
			'amount': amount,
			'secret_key': secret_key,
			'checksum': checksum,
			'game_id': game_id,
			'game': game,
			'payment' : Id,
			'current_host': current_host
		}

		# sending context to payment-template
		return render(request, 'gameview/payment.html', context)
	# If user owns game, redirect to home page.
	else:
		# redirecting to frontpage
		return redirect('/')

# Handles what happens after payment is received, if it was successful
@login_required
def successful_payment(request, game_id):
	print(game_id)
	game = Game.objects.get(id=game_id)
	current_user = request.user

	context = {
		'game': game,
	}

	if request.user.is_authenticated():
		user = User.objects.get(id=current_user.id)
		bought_game = BoughtGames(game = game, user = user)
		bought_game.save()

		return render(request, 'gameview/success.html', context)
	else:
		return render(request, 'gameview/error.html', context)

# Handles what happens after payment is received, if there was an error
@login_required
def error_payment(request, game_id):
	# payment ID
	pid = request.GET['pid']
	# game_id from pid
	game_id = pid.split('-')[1]
	game = Game.objects.get(id=game_id)
	context = {
		'game': game,
	}

	return render(request, 'gameview/error.html', context)

# Handles what happens after payment is received, if it was canceled
@login_required
def cancel_payment(request, game_id):
	# payment ID
	pid = request.GET['pid']
	# game_id from pid
	game_id = pid.split('-')[1]
	game = Game.objects.get(id=game_id)
	context = {
		'game': game,
	}

	return render(request, 'gameview/cancel.html', context)

# Handles what happens after payment is received, if it was canceled
@login_required
def rating_game(request, game_id):
	rate = request.POST['rate']
	reviews = request.POST['reviews']
	print(rate)
	print(reviews)
	gamename = Game.objects.all().filter(id=game_id).values()[0]['name']
	print(gamename)
	Username = request.user.username
	print(Username)
	newreview = ratings(player=Username, review=reviews, rating=rate, game=gamename)
	newreview.save()

	# Checks what game is being currently viewed from the id
	try:
		current_game = Game.objects.get(id=game_id)
	except Game.DoesNotExist:
		raise Http404("Game does not exist")

	# Gets users id
	user_id = request.user.id

	# Retrieves global top five scores associated with this game
	high_score_list = HighScore.objects.all().filter(game=current_game).order_by('-score')[:5]

	# Checks if user owns or has developed this game, True if does, False if not
	if request.user.is_authenticated():
		user_owns_game = len(BoughtGames.objects.all().filter(game=current_game).filter(user=request.user)) > 0
		user_developed_game = len(Game.objects.all().filter(name=current_game.name).filter(developer_id=user_id)) > 0
	else:
		user_owns_game = False
		user_developed_game = False

	print("------------------")
	mydata = ratings.objects.all().filter(game=gamename)
	print(mydata)
	print("------------------")

	context = {'object_list':mydata, 'game': current_game, 'high_scores': high_score_list, 'owned': user_owns_game, 'developed': user_developed_game, 'logged_in': request.user.is_authenticated(), 'game_id': game_id}
	return render(request, 'gameview/index.html', context)

@login_required
def get_otp(request):
	import random
	number = random.randint(1000,9999)
	number = str(number)
	from twilio.rest import Client
	account_sid = 'ACc2247aac5dd488e8b68a9f991610d749'
	auth_token = '46a4f987884ee15f62d5e7fba59fe0fb'
	client = Client(account_sid, auth_token)
	message = client.messages.create(
		body="one time password to change your password {}".format(number),
		from_='+16562230942',
		to='+9197409 36895'
	)
	print(f"Message sent with SID: {message.sid}")

	print("otp: ", number)
	f = open('OTP.txt', 'w')
	f.write(number)
	f.close()
	return redirect('/')

@login_required
def change_pass(request):
	psw = request.GET['psw']
	otp_1 = request.GET['otp']
	print(psw)
	print(otp_1)
	f = open('OTP.txt', 'r')
	otp_2 = f.read()
	f.close()
	print(otp_2)
	if int(otp_1) == int(otp_2):
		current_user = request.user
		user = User.objects.get(id=current_user.id)
		user.set_password(psw)
		user.save()
		os.remove('OTP.txt')
		from twilio.rest import Client
		account_sid = 'ACc2247aac5dd488e8b68a9f991610d749'
		auth_token = '46a4f987884ee15f62d5e7fba59fe0fb'
		client = Client(account_sid, auth_token)
		message = client.messages.create(
			body="successfully changed password",
			from_='+16562230942',
			to='+9197409 36895'
		)
		print(f"Message sent with SID: {message.sid}")
		return redirect('/auth/logout')
	else:
		return redirect('/')