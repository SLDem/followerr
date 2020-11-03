from django import forms
from .models import Message, Chat, PrivateMessage
from emoji_picker.widgets import EmojiPickerTextareaAdmin



class NewMessageForm(forms.ModelForm):
    body = forms.CharField(widget=EmojiPickerTextareaAdmin(attrs={'class': 'message-body-input',
                                                                  'style': 'resize:none;',
                                                                  'placeholder': 'Write your message'}), label="")
    image = forms.ImageField(required=False, label='',
                             widget=forms.FileInput(attrs={'class': 'message-image-input'}))

    class Meta:
        model = Message
        fields = ('body', 'image', )


class NewPrivateMessageForm(forms.ModelForm):
    body = forms.CharField(widget=EmojiPickerTextareaAdmin(attrs={'class': 'message-body-input',
                                                                  'style': 'resize:none;',
                                                                  'placeholder': 'Write your message'}), label="")
    image = forms.ImageField(required=False, label='',
                             widget=forms.FileInput(attrs={'class': 'message-image-input'}))

    class Meta:
        model = PrivateMessage
        fields = ('body', 'image', )


class NewChatForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'new-chat-form',
                                                          'placeholder': 'Enter a title to create a new chat'}),
                            label='')
    image = forms.ImageField(required=False, label='Add chat picture:',
                             widget=forms.FileInput(attrs={'class': 'message-image-input'}))

    class Meta:
        model = Chat
        fields = ('title', 'image', )


class AddUserToChatForm(forms.ModelForm):

    class Meta:
        model = Chat
        fields = ('users', )

    def __init__(self, queryset, *args, **kwargs):
        self.queryset = queryset
        super(AddUserToChatForm, self).__init__(*args, **kwargs)
        self.fields['users'] = forms.ModelMultipleChoiceField(queryset=self.queryset,
                                                              widget=forms.CheckboxSelectMultiple
                                                              (attrs={'class': 'add-people-to-chat-form'}),
                                                              label='Friends:')