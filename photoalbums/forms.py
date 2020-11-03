from django import forms
from .models import Photoalbum, Image
from emoji_picker.widgets import EmojiPickerTextInput


class NewPhotoalbumForm(forms.ModelForm):
    title = forms.CharField(widget=EmojiPickerTextInput(attrs={'class': 'new-photoalbum-title', 'style':
                                                               'resize: none;',
                                                               'placeholder': 'Enter a title for your album'}),
                            label='')

    class Meta:
        model = Photoalbum
        fields = ('title', )


class NewImageForm(forms.ModelForm):
    description = forms.CharField(widget=EmojiPickerTextInput(attrs={'class': 'new-image-title', 'style':
                                                                     'resize: none;',
                                                                     'placeholder': 'Enter a description for your image'}),
                                  label='')

    picture = forms.ImageField(required=True, label='',
                               widget=forms.FileInput(attrs={'class': 'new-picture-input'}))

    class Meta:
        model = Image
        fields = ('description', 'picture')
