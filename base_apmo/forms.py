from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import Category, Preacher, Playlist, Sermon


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

class SermonForm(ModelForm):
    class Meta:
        model = Sermon
        fields = '__all__'