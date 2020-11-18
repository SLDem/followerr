from django import forms
from posts.models import Post
from emoji_picker.widgets import EmojiPickerTextareaAdmin


class NewPostForm(forms.ModelForm):
    body = forms.CharField(widget=EmojiPickerTextareaAdmin(attrs={'class': 'post-body-input',
                                                                  'style': 'resize:none;',
                                                                  'placeholder': 'What would you like to post?'}),
                           label="")
    image = forms.ImageField(required=False, label='',
                             widget=forms.FileInput(attrs={'class': 'post-image-input'}))


    class Meta:
        model = Post
        fields = ('body', 'image')
