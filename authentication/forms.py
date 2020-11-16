from django.contrib.auth.forms import UserCreationForm
from django import forms
from user_profile.models import User


class SignupForm(UserCreationForm):
    gender = forms.NullBooleanField(widget=forms.Select(attrs={'class': 'signup-gender'}, choices=[
        (True, 'Male'),
        (False, 'Female')
    ]))

    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'signup-email'}))
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'signup-name'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'signup-password'}), label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'signup-password'}), label='Confirm Password')

    class Meta:
        model = User
        fields = ('email', 'name', 'gender', )
