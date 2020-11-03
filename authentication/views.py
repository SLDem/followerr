from django.shortcuts import render, redirect, reverse
from django.core.mail import EmailMessage
from django.contrib import messages
from django.contrib.auth import authenticate

from datetime import timedelta
from django.views import View
import online_users.models

from .utils import token_generator
from .forms import SignupForm
from user_profile.models import User

from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site


def see_online_users():
    user_status = online_users.models.OnlineUserActivity.get_user_activities(timedelta(seconds=300))
    users = list((user.user for user in user_status))
    return users


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            raw_password = form.cleaned_data.get('password1')
            name = form.cleaned_data['name']
            gender = form.cleaned_data['gender']
            user.is_active = False
            user = User.objects.create(email=user.email, password=raw_password, name=name, gender=gender)
            user.set_password(raw_password)
            user.save()

            email_subject = 'Activate your followerr account'

            domain = get_current_site(request).domain

            user_id = urlsafe_base64_encode(force_bytes(user.pk))

            link = reverse('activate', kwargs={
                'user_id': user_id,
                'token': token_generator.make_token(user),
            })

            activate_url = 'http://' + domain + link

            email_body = 'Hello ' + user.name + ' please use this link to verify your account\n' + activate_url

            email = EmailMessage(
                email_subject,
                email_body,
                'noreply@semicolon.com',
                [user.email],

            )
            email.send()

            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


class VerificationView(View):
    def get(self, request, user_id, token):
        try:
            id = urlsafe_base64_decode(force_text(user_id))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user, token):
                return redirect('login')
            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()
            messages.success(request, 'Account activated successfully')
            return redirect('login')
        except Exception as ex:
            pass
        return redirect('login')
