from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate

from datetime import timedelta

import online_users.models
from django_email_verification import sendConfirm

from .forms import SignupForm


def see_online_users():
    user_status = online_users.models.OnlineUserActivity.get_user_activities(timedelta(seconds=300))
    users = list((user.user for user in user_status))
    return users


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(request, email=user.email, password=raw_password)
            sendConfirm(user)
            if user is not None:
                login(request, user)
            else:
                print('User is not authenticated')
            return redirect('profile', pk=request.user.pk)
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})
