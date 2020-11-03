from django import forms
from comments.models import Comment
from emoji_picker.widgets import EmojiPickerTextareaAdmin


class NewCommentForm(forms.ModelForm):
    body = forms.CharField(widget=EmojiPickerTextareaAdmin(attrs={'class': 'comment-body-input',
                                                                  'style': 'resize:none;',
                                                                  'placeholder': 'Reply...'}),
                           label='')

    class Meta:
        model = Comment
        fields = ('body', )
