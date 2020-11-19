from django.shortcuts import render, redirect, reverse, HttpResponse
from django.core.mail import EmailMessage
from django.contrib import messages
from django.forms import forms

from datetime import timedelta
from django.views import View
# from django.views.generic import TemplateView
import online_users.models

from .utils import token_generator
from .forms import SignupForm, PasswordResetForm, PasswordResetEmailForm
from user_profile.models import User

from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site


def see_online_users():
    user_status = online_users.models.OnlineUserActivity.get_user_activities(timedelta(seconds=300))
    users = list((user.user for user in user_status))
    return users


def signup(request):
    title = 'Signup'
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

            # Verification
            email_subject = 'Activate your followerr account'
            domain = get_current_site(request).domain
            user_id = urlsafe_base64_encode(force_bytes(user.pk))
            link = reverse('activate', kwargs={
                'user_id': user_id,
                'token': token_generator.make_token(user),
            })
            activate_url = 'http://' + domain + link
            email_body = 'Hello ' + user.name + \
                         ' please use this link to verify your followerr account\n' + activate_url
            email = EmailMessage(
                email_subject,
                email_body,
                'noreply@followerr.com',
                [user.email],
            )
            email.send()
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'authentication/custom_signup.html', {'form': form, 'title': title})


class VerificationView(View):
    def get(self, request, user_id, token):
        try:
            id = urlsafe_base64_decode(force_text(user_id))
            user = User.objects.get(pk=id)
            if not token_generator.check_token(user, token):
                return HttpResponse('login failed')
            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()
            messages.success(request, 'Account activated successfully')
            return redirect('login')
        except Exception as ex:
            print(ex)
        return redirect('login')


def password_reset(request):
    title = 'Reset Password'
    if request.method == 'POST':
        form = PasswordResetEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)
            email_subject = 'Reset your followerr password'
            domain = get_current_site(request).domain
            user_id = urlsafe_base64_encode(force_bytes(user.pk))
            link = reverse('confirm_password_reset', kwargs={
                'user_id': user_id,
                'token': token_generator.make_token(user)
            })
            reset_url = 'http://' + domain + link
            email_body = 'Hello ' + user.name + \
                ' please use this link to reset your followerr password\n' + reset_url
            email = EmailMessage(
                email_subject,
                email_body,
                'noreply@followerr.com',
                [user.email]
            )
            email.send()
            return HttpResponse('Please go to your email and use the link that was sent to reset your password')
    else:
        form = PasswordResetEmailForm()
    return render(request, 'authentication/password_reset_email.html', {'form': form, 'title': title})


def password_reset_view(request, user_id, token):
    id = urlsafe_base64_decode(force_text(user_id))
    user = User.objects.get(pk=id)
    if not token_generator.check_token(user, token):
        return HttpResponse('Reset password attempt failed')
    form = PasswordResetForm(request.POST)
    if form.is_valid():
        password1 = form.cleaned_data['password1']
        password2 = form.cleaned_data['password2']
        if password1 == password2:
            user.set_password(password1)
            user.save()
            return redirect('login')
        else:
            raise forms.ValidationError("Passwords must be identical.")
    return render(request, 'authentication/password_reset.html', {'form': form})

