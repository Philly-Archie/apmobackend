from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import Category, Preacher, Playlist, Sermon, Bookmark, Favourite, Events, Devotion


class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

class PreacherForm(ModelForm):
    class Meta:
        model = Preacher
        fields = '__all__'


class PlaylistForm(ModelForm):
    class Meta:
        model = Playlist
        fields = '__all__'

# class SermonForm(ModelForm):
#     class Meta:
#         model = Sermon
#         fields = '__all__'


# class SermonForm(forms.Form):
#     preacher = forms.ChoiceField(choices=[], required=True)
#     category = forms.ChoiceField(choices=[], required=True)
#     playlists = forms.MultipleChoiceField(choices=[], required=False)

#     def __init__(self, *args, **kwargs):
#         preachers = kwargs.pop('preachers', [])
#         categories = kwargs.pop('categories', [])
#         playlists = kwargs.pop('playlists', [])
#         super(SermonForm, self).__init__(*args, **kwargs)
        
#         self.fields['preacher'].choices = [(preacher['id'], preacher['name']) for preacher in preachers]
#         self.fields['category'].choices = [(category['id'], category['name']) for category in categories]
#         self.fields['playlists'].choices = [(playlist['id'], playlist['name']) for playlist in playlists]



class SermonForm(forms.Form):
    title = forms.CharField(max_length=200, required=True)
    preacher = forms.ChoiceField(choices=[], required=True)
    category = forms.ChoiceField(choices=[], required=True)
    playlists = forms.MultipleChoiceField(choices=[], required=False)
    description = forms.CharField(widget=forms.Textarea, required=True)
    duration = forms.DurationField(required=True)
    date_published = forms.DateField(required=True)
    topic = forms.CharField(max_length=200, required=True)
    tags = forms.CharField(max_length=200, required=True)
    language = forms.CharField(max_length=50, required=True)
    play_count = forms.IntegerField(required=False)
    likes_count = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        preachers = kwargs.pop('preachers', [])
        categories = kwargs.pop('categories', [])
        playlists = kwargs.pop('playlists', [])
        super(SermonForm, self).__init__(*args, **kwargs)
        
        self.fields['preacher'].choices = [(preacher['id'], preacher['name']) for preacher in preachers]
        self.fields['category'].choices = [(category['id'], category['name']) for category in categories]
        self.fields['playlists'].choices = [(playlist['id'], playlist['name']) for playlist in playlists]


class FavouriteForm(ModelForm):
    class Meta:
        model = Favourite
        fields = '__all__'

class BookmarkForm(ModelForm):
    class Meta:
        model = Bookmark
        fields = '__all__'

class EventsForm(ModelForm):
    class Meta:
        model = Events
        fields = '__all__'

class DevotionForm(ModelForm):
    class Meta:
        model = Devotion
        fields = '__all__'