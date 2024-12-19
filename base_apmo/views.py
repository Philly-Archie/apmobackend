from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from .forms import CategoryForm, PreacherForm, PlaylistForm, SermonForm
from .models import Category, Preacher, Playlist, Sermon, Download, Favourite, Bookmark, Events, Devotion
from django.db.models import Count, Q

from base_apmo.forms import SignUpForm

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import SermonSerializer, DevotionSerializer, EventsSerializer

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from django.db import IntegrityError

# Create your views here.

def signup(request):
    form = SignUpForm()
    context = {
        'username': '',
        'password1': '',
        'password2': '',
        'email': '',
        'form': form,
    }

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        context['username'] = request.POST.get('username')
        context['password1'] = request.POST.get('password1')
        context['password2'] = request.POST.get('password2')
        context['email'] = request.POST.get('email')
        context['form'] = form

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            form.save()
            new_user = authenticate(username=username, password=password)
            if new_user is not None:
                login(request, new_user)
                return redirect("home")
        else:
            messages.error(request, form.errors)
    
    return render(request, "auth/signup.html", context)

def logoutUser(request):
    logout(request)
    return redirect('login')

def loginPage(request):
    context = {
        'username': '',
        'password': ''
    }
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        context['username'] = username
        context['password'] = password

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Invalid Credentials')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Wrong credentials')

    return render(request, 'auth/login.html', context)

        

@login_required
def home(request):
    sermons = Sermon.objects.all()
    total_sermons = Sermon.objects.count()
    total_audio_sermons = Sermon.objects.filter(~Q(audio_file="")).count()

    context = {
        'sermons': sermons,
        'total_sermons': total_sermons,
        'total_audio_sermons': total_audio_sermons
    }
    return render(request, "dashboard.html", context)


@login_required
def categories(request):
    categories = Category.objects.all()
    preachers = Preacher.objects.all()
    playlists = Playlist.objects.all()
    context = {
        'categories' : categories,
        'preachers' : preachers,
        'playlists' : playlists,
    }
    return render(request, 'sermons/category.html', context)


@login_required
def createCategory(request):
    form = CategoryForm
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            messages.success(request, "Category has been created")
            form.save()
            return redirect('categories')
    return render(request, 'sermons/add_category_form.html')

@login_required
def createPreacher(request):
    form = PreacherForm()
    if request.method == 'POST':
        form = PreacherForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Preacher has been added")
            return redirect('categories')
        else:
            messages.error(request, "Please correct the errors below.")
    
    return render(request, 'sermons/add_preacher_form.html', {'form': form})


@login_required
def createPlaylist(request):
    form = PlaylistForm
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            messages.success(request, "Playlist has been created")
            form.save()
            return redirect('categories')
    return render(request, 'sermons/add_playlist_form.html')


@login_required
def createSermon(request):
    form = SermonForm
    preachers = Preacher.objects.all()
    categories = Category.objects.all()
    playlists = Playlist.objects.all()

    context = {
        'preachers': preachers,
        'categories': categories,
        'playlists': playlists,
        'form' : form
    }

    if request.method == 'POST':
        form = SermonForm(request.POST, request.FILES)
        if form.is_valid():
            messages.success(request, "Sermon has been created")
            form.save()
            return redirect('home')
        else:
            print("Form errors:")
            for field, errors in form.errors.items():
                print(f"{field}: {errors}")
    
    return render(request, 'sermons/add_sermons_form.html', context)


@login_required(login_url='/login')
def editCategory(request, pk):
    category = Category.objects.get(id=pk)
    context = {
        'category': category
    }

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            messages.success(request, "Category has been edited")
            form.save()
            return redirect('categories')
    return render(request, 'sermons/edit_category.html', context)


@login_required(login_url='/login')
def deleteCategory(request, pk):
    category = Category.objects.get(id=pk)
    context = {
        'category': category
    }
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category has been deleted")
        return redirect('categories')
    return render(request, 'sermons/delete_category.html', context)

@login_required
def editPreacher(request, pk):
    preacher = Preacher.objects.get(id=pk)
    context = {
        'preacher' : preacher,
    }

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=preacher)
        if form.is_valid():
            messages.success(request, "Preacher has been edited successfully")
            form.save()
            return redirect("categories")
        
    return render(request, "sermons/edit_preacher.html", context)


@login_required(login_url='/login')
def deletePreacher(request, pk):
    preacher = Preacher.objects.get(id=pk)
    context = {
        'preacher': preacher
    }
    if request.method == 'POST':
        preacher.delete()
        messages.success(request, "Preacher has been deleted")
        return redirect('categories')
    return render(request, 'sermons/delete_preacher.html', context)


@login_required
def editPlaylist(request, pk):
    playlist = Playlist.objects.get(id=pk)
    context = {
        'playlist' : playlist,
    }

    if request.method == "POST":
        form = PlaylistForm(request.POST, instance=playlist)
        if form.is_valid():
            messages.success(request, "Playlist has been edited successfully")
            form.save()
            return redirect("categories")
        
    return render(request, "sermons/edit_playlist.html", context)


@login_required(login_url='/login')
def deletePlaylist(request, pk):
    playlist = Playlist.objects.get(id=pk)
    context = {
        'playlist': playlist
    }
    if request.method == 'POST':
        playlist.delete()
        messages.success(request, "Playlist has been deleted")
        return redirect('categories')
    return render(request, 'sermons/delete_playlist.html', context)


@login_required
def editSermon(request, pk):
    sermon = Sermon.objects.get(id=pk)
    preachers = Preacher.objects.all()
    categories = Category.objects.all()
    playlists = Playlist.objects.all()

    if request.method == "POST":
        form = SermonForm(request.POST, request.FILES, instance=sermon)
        if form.is_valid():
            form.save()
            messages.success(request, "Sermon has been edited successfully")
            return redirect("home")
        else:
            print("Form errors:", form.errors)  # Debugging form errors
    else:
        form = SermonForm(instance=sermon)

    context = {
        'sermon': sermon,
        'preachers': preachers,
        'categories': categories,
        'playlists': playlists,
        'form': form,
    }

    return render(request, "sermons/edit_sermons.html", context)



@login_required(login_url='/login')
def deleteSermon(request, pk):
    sermon = Sermon.objects.get(id=pk)
    context = {
        'sermon': sermon
    }
    if request.method == 'POST':
        sermon.delete()
        messages.success(request, "Sermon has been deleted")
        return redirect('home')
    return render(request, 'sermons/delete_sermons.html', context)


# Events and devotionals
@login_required
def events(request):
    # categories = Category.objects.all()
    # preachers = Preacher.objects.all()
    # playlists = Playlist.objects.all()
    # context = {
    #     'categories' : categories,
    #     'preachers' : preachers,
    #     'playlists' : playlists,
    # }
    return render(request, 'events/events.html')

@login_required
def createDevotional(request):
    form = DevotionalForm()

    if request.method == 'POST':
        form = DevotionalForm(request.POST, request.FILES)
        if form.is_valid():
            messages.success(request, "Devotional has been created")
            form.save()
            return redirect('devotionals')
        else:
            for field, errors in form.errors.items():
                print(f"{field}: {errors}")

    return render(request, 'event/add_devotionals_form.html')

@login_required
def createEvent(request):
    form = EventForm()

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            messages.success(request, "Event has been created")
            form.save()
            return redirect('events')
        else:
            for field, errors in form.errors.items():
                print(f"{field}: {errors}")

    return render(request, 'events/add_events_form.html', context)


@login_required(login_url='/login')
def editDevotional(request, pk):
    devotional = Devotional.objects.get(id=pk)
    form = DevotionalForm(instance=devotional)

    if request.method == 'POST':
        form = DevotionalForm(request.POST, request.FILES, instance=devotional)
        if form.is_valid():
            messages.success(request, "Devotional has been edited")
            form.save()
            return redirect('devotionals')

    context = {'form': form, 'devotional': devotional}
    return render(request, 'events/edit_devotional.html', context)

@login_required(login_url='/login')
def editEvent(request, pk):
    event = Event.objects.get(id=pk)
    form = EventForm(instance=event)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            messages.success(request, "Event has been edited")
            form.save()
            return redirect('events')

    context = {'form': form, 'event': event}
    return render(request, 'events/edit_event.html', context)


@login_required(login_url='/login')
def deleteDevotional(request, pk):
    devotional = Devotional.objects.get(id=pk)

    if request.method == 'POST':
        devotional.delete()
        messages.success(request, "Devotional has been deleted")
        return redirect('devotionals')

    context = {'devotional': devotional}
    return render(request, 'events/delete_devotional.html', context)
@login_required(login_url='/login')


def deleteEvent(request, pk):
    event = Event.objects.get(id=pk)

    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event has been deleted")
        return redirect('events')

    context = {'event': event}
    return render(request, 'events/delete_event.html', context)



################################
# Api Views
class SermonListView(APIView):
    def get(self, request):
        sermons = Sermon.objects.all()
        serializer = SermonSerializer(sermons, many=True, context={'request': request})
        return Response(serializer.data)

class DevotionListView(APIView):
    def get(self, request):
        devotions = Devotion.objects.all()
        serializer = DevotionSerializer(devotions, many=True, context={'request': request})
        return Response(serializer.data)

class EventsListView(APIView):
    def get(self, request):
        events = Events.objects.all()
        serializer = EventsSerializer(events, many=True, context={'request': request})
        return Response(serializer.data)


#########################################
# End of API views




# Generic helper function for creating objects with duplicate checks
def create_object(model, user, sermon_id):
    sermon = get_object_or_404(Sermon, id=sermon_id)
    try:
        obj, created = model.objects.get_or_create(user=user, sermon=sermon)
        if created:
            return obj, "Object created successfully"
        return obj, "Object already exists"
    except IntegrityError:
        return None, "Integrity error occurred"

# View for managing downloads
class DownloadView(View):
    def get(self, request, user_id):
        downloads = Download.objects.filter(user__id=user_id)
        data = [
            {
                'id': d.id,
                'sermon': d.sermon.id,
                'download_date': d.download_date,
            }
            for d in downloads
        ]
        return JsonResponse({'downloads': data}, status=200)

    def post(self, request, user_id, sermon_id):
        user = get_object_or_404(User, id=user_id)
        download, message = create_object(Download, user, sermon_id)
        if download:
            return JsonResponse({'message': message, 'id': download.id}, status=201)
        return JsonResponse({'message': message}, status=400)

# View for managing favourites
class FavouriteView(View):
    def get(self, request, user_id):
        favourites = Favourite.objects.filter(user__id=user_id)
        data = [
            {
                'id': f.id,
                'sermon': f.sermon.id,
                'favourited_date': f.favourited_date,
            }
            for f in favourites
        ]
        return JsonResponse({'favourites': data}, status=200)

    def post(self, request, user_id, sermon_id):
        user = get_object_or_404(User, id=user_id)
        favourite, message = create_object(Favourite, user, sermon_id)
        if favourite:
            return JsonResponse({'message': message, 'id': favourite.id}, status=201)
        return JsonResponse({'message': message}, status=400)

# View for managing bookmarks
class BookmarkView(View):
    def get(self, request, user_id):
        bookmarks = Bookmark.objects.filter(user__id=user_id)
        data = [
            {
                'id': b.id,
                'sermon': b.sermon.id,
                'bookmarked_date': b.bookmarked_date,
            }
            for b in bookmarks
        ]
        return JsonResponse({'bookmarks': data}, status=200)

    def post(self, request, user_id, sermon_id):
        user = get_object_or_404(User, id=user_id)
        bookmark, message = create_object(Bookmark, user, sermon_id)
        if bookmark:
            return JsonResponse({'message': message, 'id': bookmark.id}, status=201)
        return JsonResponse({'message': message}, status=400)

# View for managing events
class EventsView(View):
    def get(self, request):
        events = Events.objects.all()
        data = [
            {
                'id': event.id,
                'title': event.title,
                'date': event.date,
                'description': event.description,
                'link': event.link,
                'event_thumbnail': event.event_thumbnail.url if event.event_thumbnail else None,
            }
            for event in events
        ]
        return JsonResponse({'events': data}, safe=False)

    def post(self, request):
        title = request.POST.get('title')
        date = request.POST.get('date')
        description = request.POST.get('description')
        link = request.POST.get('link')
        event_thumbnail = request.FILES.get('event_thumbnail')

        event = Events.objects.create(
            title=title,
            date=date,
            description=description,
            link=link,
            event_thumbnail=event_thumbnail
        )
        return JsonResponse({'message': 'Event created', 'id': event.id}, status=201)

# View for managing devotions
class DevotionView(View):
    def get(self, request):
        devotions = Devotion.objects.all()
        data = [
            {
                'id': devotion.id,
                'title': devotion.title,
                'theme_scripture': devotion.theme_scripture,
                'content': devotion.content,
                'devotion_thumbnail': devotion.devotion_thumbnail.url if devotion.devotion_thumbnail else None,
            }
            for devotion in devotions
        ]
        return JsonResponse({'devotions': data}, safe=False)

    def post(self, request):
        title = request.POST.get('title')
        theme_scripture = request.POST.get('theme_scripture')
        content = request.POST.get('content')
        devotion_thumbnail = request.FILES.get('devotion_thumbnail')

        devotion = Devotion.objects.create(
            title=title,
            theme_scripture=theme_scripture,
            content=content,
            devotion_thumbnail=devotion_thumbnail
        )
        return JsonResponse({'message': 'Devotion created', 'id': devotion.id}, status=201)

