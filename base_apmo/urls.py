from django.urls import path
# from django.contrib.auth import views as auth_views
from . import views

from django.conf import settings
from django.conf.urls.static import static
from .views import SermonListView
from .views import SermonListView, DownloadView, FavouriteView, BookmarkView, EventsView, DevotionView

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path("signup/", views.signup, name="signup"),
    path("categories/", views.categories, name="categories"),
    path('sermons/create-category', views.createCategory, name='create_category'),
    path('sermons/create-preacher', views.createPreacher, name='create_preacher'),
    path('sermons/create-playlist', views.createPlaylist, name='create_playlist'),
    path('sermons/create-sermons', views.createSermon, name='create_sermon'),
    path('sermons/edit-category/<str:pk>/', views.editCategory, name='edit_category'),
    path('sermons/delete-category/<str:pk>/', views.deleteCategory, name='delete_category'),
    path('sermons/edit-preacher/<str:pk>/', views.editPreacher, name='edit_preacher'),
    path('sermons/delete-preacher/<str:pk>/', views.deletePreacher, name='delete_preacher'),
    path('sermons/edit-playlist/<str:pk>/', views.editPlaylist, name='edit_playlist'),
    path('sermons/delete-playlist/<str:pk>/', views.deletePlaylist, name='delete_playlist'),
    path('sermons/edit-sermon/<str:pk>/', views.editSermon, name='edit_sermon'),
    path('sermons/delete-sermon/<str:pk>/', views.deleteSermon, name='delete_sermon'),

    # Events and devotionals
    path("events/", views.events, name="events"),
    path('devotionals/create/', views.createDevotional, name='create_devotional'),
    path('devotionals/edit/<int:pk>/', views.editDevotional, name='edit_devotional'),
    path('devotionals/delete/<int:pk>/', views.deleteDevotional, name='delete_devotional'),
    path('events/create/', views.createEvent, name='create_event'),
    path('events/edit/<int:pk>/', views.editEvent, name='edit_event'),
    path('events/delete/<int:pk>/', views.deleteEvent, name='delete_event'),



    path('downloads/<int:user_id>/', DownloadView.as_view(), name='downloads-list'),
    path('downloads/<int:user_id>/<int:sermon_id>/', DownloadView.as_view(), name='download-add'),
    path('favourites/<int:user_id>/', FavouriteView.as_view(), name='favourites-list'),
    path('favourites/<int:user_id>/<int:sermon_id>/', FavouriteView.as_view(), name='favourite-add'),
    path('bookmarks/<int:user_id>/', BookmarkView.as_view(), name='bookmarks-list'),
    path('bookmarks/<int:user_id>/<int:sermon_id>/', BookmarkView.as_view(), name='bookmark-add'),
    path('events/', EventsView.as_view(), name='events-list'),
    path('events/create/', EventsView.as_view(), name='event-create'),
    path('devotions/', DevotionView.as_view(), name='devotions-list'),
    path('devotions/create/', DevotionView.as_view(), name='devotion-create'),


    # Api Urls
    path('api/sermons/', SermonListView.as_view(), name='sermon-list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)