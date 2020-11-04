from django import forms
from groups.models import Group, Discussion
from emoji_picker.widgets import EmojiPickerTextareaAdmin



class NewGroupForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'group-title-input', 'placeholder': 'Enter title'}),
                            label='')
    description = forms.CharField(widget=EmojiPickerTextareaAdmin(attrs={'class': 'group-description-input',
                                                                         'placeholder': 'Enter group description'}),
                                  label='')
    image = forms.ImageField(required=False, label='Upload group avatar',
                                    widget=forms.FileInput(attrs={'class': 'group-avatar-input',
                                                                  'placeholder': 'Add image'}))

    class Meta:
        model = Group
        fields = ('title', 'description', 'image', 'is_private')





class NewDiscussionForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'discussion-title',
                                                          'placeholder': 'Enter a title for your discussion...'}),
                            label='')
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'discussion-description',
                                                               'placeholder': 'Describe here...'}),
                                  label='')

    class Meta:
        model = Discussion
        fields = ('title', 'description', )
