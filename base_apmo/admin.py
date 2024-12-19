from django.contrib import admin
from .models import Category, Preacher, Playlist, Sermon, Favourite, Bookmark, Devotion, Events
# Register your models here.

admin.site.register(Category)
admin.site.register(Preacher)
admin.site.register(Playlist)
admin.site.register(Sermon)
admin.site.register(Favourite)
admin.site.register(Bookmark)
admin.site.register(Devotion)
admin.site.register(Events)