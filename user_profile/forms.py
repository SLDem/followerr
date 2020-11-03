from django import forms
from user_profile.models import User
from emoji_picker.widgets import EmojiPickerTextareaAdmin


class EditUserForm(forms.ModelForm):
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'email'}), label='Your email:')
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'name'}), label='Your name:')
    following = forms.CharField(widget=forms.TextInput(attrs={'class': 'following'}), label='You are following:')

    about_me = forms.CharField(widget=EmojiPickerTextareaAdmin(attrs={
        'class': 'about_me',
        'placeholder': 'Write about yourself...'}),
                               label='About you:')
    favourite_music = forms.CharField(widget=EmojiPickerTextareaAdmin(attrs={
        'class': 'favourite_music',
        'placeholder': 'Write about the music you like...'}),
                                      label='Your favourite music:')
    favourite_books = forms.CharField(widget=EmojiPickerTextareaAdmin(attrs={
        'class': 'favourite_books',
        'placeholder': 'Write about your favourite books or authors...'}),
                                      label='Your favourite books')
    favourite_movies = forms.CharField(widget=EmojiPickerTextareaAdmin(attrs={
        'class': 'favourite_movies',
        'placeholder': 'Write about your favourite movies or directors...'}),
                                       label='Your favourite movies')

    gender = forms.NullBooleanField(widget=forms.Select(choices=[
        ('', 'Unknown'),
        (True, 'Male'),
        (False, 'Female')
    ], attrs={'class': 'gender'}))

    class Meta:
        model = User
        fields = ('following', 'email', 'name', 'city', 'about_me', 'favourite_music', 'favourite_books',
                  'favourite_movies', 'gender', )


class ChangePasswordForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('password', 'confirm_password')