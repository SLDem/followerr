from django.contrib.auth.forms import UserCreationForm
from django import forms
from user_profile.models import User


class SignupForm(UserCreationForm):
    gender = forms.NullBooleanField(widget=forms.Select(choices=[
        (True, 'Male'),
        (False, 'Female')
    ]))

    class Meta:
        model = User
        fields = ('email', 'name', 'gender', )
