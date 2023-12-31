from django.shortcuts import render, redirect
from django.template import loader
from .models import Game, BoughtGames, Category
from django.contrib.auth.models import User
from itertools import chain
from registration.models import Profile
from .forms import UserTypeForm
from django.contrib.auth.models import Group
import os
def index(request):
    most_recent_game = Game.objects.order_by('price')
    games = most_recent_game
    user_id = request.user.id
    # Retrieve all categories
    categories = Category.objects.all()
    user_has_profile = True
    form = UserTypeForm()

    current_host = request.META.get('HTTP_HOST')

    # If user has logged in using OAuth
    if request.user.is_authenticated and len(Profile.objects.all().filter(user=request.user)) == 0:
        user_has_profile = False
        # handling form actions
        if request.method == 'POST':
            form = UserTypeForm(request.POST)
            if form.is_valid():
                # Creating a profile for the user
                user = request.user
                user_type = form.cleaned_data.get('user_type')
                this_user = Profile.objects.create(user=user, activation_key='not_needed_with_oauth', user_type=user_type, is_activated=True)
                this_user.save()
                group = Group.objects.get(name=user_type)
                user.groups.add(group)
                return redirect("/")
        else:
            # Insert the UserTypeForm
            form = UserTypeForm()

    if request.user.is_authenticated:
        bought_games = []
        # getting game models from user's bought games
        for bought_game in BoughtGames.objects.all().filter(user=request.user):
            bought_games.append(bought_game.game)

        # games the user has developed
        developed_games = Game.objects.all().filter(developer_id=user_id)
        # combining bought and developed games
        combined_games = list(chain(bought_games, developed_games))
        # removing possible duplicate games from set
        owned_games = list(set(combined_games))
    else:
        owned_games = BoughtGames.objects.none()

    if os.path.exists('OTP.txt'):
        context = {
        'games': games,
        'id': 123,  # Replace with the actual value for 'id'
        'owned_games': owned_games,
        'categories': categories,
        'user_has_profile': user_has_profile,
        'form': form,
        'current_host': current_host,
        'otp': True
        }
        return render(request, 'store/index.html', context)
    else:
        context = {
        'games': games,
        'id': 123,  # Replace with the actual value for 'id'
        'owned_games': owned_games,
        'categories': categories,
        'user_has_profile': user_has_profile,
        'form': form,
        'current_host': current_host,
        'otp': False
        }
        return render(request, 'store/index.html', context)