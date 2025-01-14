from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from .forms import CategoryForm, PreacherForm, PlaylistForm, SermonForm, EventsForm, DevotionForm
from .models import Category, Preacher, Playlist, Sermon, Download, Favourite, Bookmark, Events, Devotion
from django.db.models import Count, Q
from datetime import datetime, date
import traceback

from base_apmo.forms import SignUpForm

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import SermonSerializer, DevotionalsSerializer, EventsSerializer, CategorySerializer

from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from django.db import IntegrityError
from google.cloud import firestore, storage
import uuid

# Initialize Firestore
db = firestore.Client()

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

        

# @login_required
# def home(request):
#     sermons = Sermon.objects.all()
#     total_sermons = Sermon.objects.count()
#     total_audio_sermons = Sermon.objects.filter(~Q(audio_file="")).count()

#     context = {
#         'sermons': sermons,
#         'total_sermons': total_sermons,
#         'total_audio_sermons': total_audio_sermons
#     }
#     return render(request, "dashboard.html", context)



@login_required
def home(request):
    try:
        # Fetch sermons from Firestore
        sermons_ref = db.collection('sermons')
        sermons_docs = sermons_ref.stream()  # Get all sermon documents

        # Convert Firestore documents to a list of dictionaries
        sermons = []
        for doc in sermons_docs:
            sermon = doc.to_dict()
            sermon['id'] = doc.id  # Add the document ID if needed
            
            # Fetch category data
            if 'category' in sermon:  # Check if category exists in the sermon document
                category = db.collection('categories').document(sermon['category']).get()
                if category.exists:
                    sermon['category'] = category.to_dict()
                else:
                    sermon['category'] = None
                    print(f"Category not found for sermon {sermon['id']}")

            # Fetch preacher data
            if 'preacher' in sermon:  # Check if preacher exists in the sermon document
                preacher = db.collection('preachers').document(sermon['preacher']).get()
                if preacher.exists:
                    sermon['preacher'] = preacher.to_dict()
                else:
                    sermon['preacher'] = None
                    print(f"Preacher not found for sermon {sermon['id']}")

            # Fetch playlists data
            if 'playlist' in sermon:  # Check if playlist exists in the sermon document
                sermon['playlists'] = []
                for playlist_id in sermon['playlist']:
                    playlist = db.collection('playlists').document(playlist_id).get()
                    if playlist.exists:
                        sermon['playlists'].append(playlist.to_dict())
            
            sermons.append(sermon)

        # Count total sermons
        total_sermons = len(sermons)

        # Count total audio sermons (where audio_file is not empty)
        total_audio_sermons = sum(1 for sermon in sermons if sermon.get('audio_file'))

        # Context for the template
        context = {
            'sermons': sermons,
            'total_sermons': total_sermons,
            'total_audio_sermons': total_audio_sermons,
        }

        return render(request, "dashboard.html", context)

    except Exception as e:
        print(f"Error retrieving sermons from Firestore: {e}")
        messages.error(request, "Failed to retrieve sermons. Please try again.")
        return render(request, "dashboard.html", {})


# @login_required
# def categories(request):
#     categories = Category.objects.all()
#     preachers = Preacher.objects.all()
#     playlists = Playlist.objects.all()
#     context = {
#         'categories' : categories,
#         'preachers' : preachers,
#         'playlists' : playlists,
#     }
#     return render(request, 'sermons/category.html', context)



@login_required
def categories(request):
    # Retrieve categories from Firebase Firestore
    categories_ref = db.collection('categories')
    categories_query = categories_ref.stream()

    categories = []
    for category in categories_query:
        category_data = category.to_dict()
        category_data['id'] = category.id
        categories.append(category_data)

    # If you have other models like Preacher and Playlist stored in Firebase as well,
    # you can retrieve them similarly
    preachers_ref = db.collection('preachers')
    preachers_query = preachers_ref.stream()

    preachers = []
    for preacher in preachers_query:
        preacher_data = preacher.to_dict()
        preacher_data['id'] = preacher.id
        preachers.append(preacher_data)

    playlists_ref = db.collection('playlists')
    playlists_query = playlists_ref.stream()

    playlists = []
    for playlist in playlists_query:
        playlist_data = playlist.to_dict()
        playlist_data['id'] = playlist.id
        playlists.append(playlist_data)

    # Pass the data to the template
    context = {
        'categories': categories,
        'preachers': preachers,
        'playlists': playlists,
    }
    return render(request, 'sermons/category.html', context)



# @login_required
# def createCategory(request):
#     form = CategoryForm
#     if request.method == 'POST':
#         form = CategoryForm(request.POST)
#         if form.is_valid():
#             category_data = form.cleaned_data

#             # Add category to Firebase
#             category_ref = db.collection('categories').add({
#                 'name': category_data['name'],
#                 'description': category_data['description'],
#                 'category_thumbnail_url': image_url,
#                 'created_at': firestore.SERVER_TIMESTAMP
#             })

#             messages.success(request, "Category has been created and stored in Firebase")
#             return redirect('categories')
#     return render(request, 'sermons/add_category_form.html')



@login_required
def createCategory(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category_data = form.cleaned_data

            # Process the uploaded image
            image_file = request.FILES.get('category_thumbnail')
            image_url = None
            if image_file:
                # Initialize Firebase Storage
                storage_client = storage.Client()
                bucket = storage_client.bucket('##')  # Replace with your bucket name
                
                # Generate a unique file name
                unique_filename = f"categories/{uuid.uuid4().hex}_{image_file.name}"
                blob = bucket.blob(unique_filename)
                
                # Upload the image file to Firebase Storage
                blob.upload_from_file(image_file.file)
                blob.make_public()  # Make the file public
                
                # Get the public URL for the image
                image_url = blob.public_url

            # Add category data to Firestore
            category_ref = db.collection('categories').add({
                'name': category_data['name'],
                'description': category_data['description'],
                'category_thumbnail_url': None,  # Add the image URL
                'created_at': firestore.SERVER_TIMESTAMP
            })

            messages.success(request, "Category has been created and stored in Firebase")
            return redirect('categories')
    
    return render(request, 'sermons/add_category_form.html', {'form': form})



# @login_required
# def createPreacher(request):
#     form = PreacherForm()
#     if request.method == 'POST':
#         form = PreacherForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Preacher has been added")
#             return redirect('categories')
#         else:
#             messages.error(request, "Please correct the errors below.")
    
#     return render(request, 'sermons/add_preacher_form.html', {'form': form})



@login_required
def createPreacher(request):
    form = PreacherForm()
    if request.method == 'POST':
        form = PreacherForm(request.POST, request.FILES)
        if form.is_valid():
            preacher_data = form.cleaned_data

            # Process the uploaded profile picture
            profile_picture = request.FILES.get('profile_picture')
            profile_picture_url = None
            if profile_picture:
                # Initialize Firebase Storage
                storage_client = storage.Client()
                # bucket = storage_client.bucket('')  # Replace with your bucket name
                
                # Generate a unique file name
                unique_filename = f"preachers/{uuid.uuid4().hex}_{profile_picture.name}"
                blob = bucket.blob(unique_filename)
                
                # Upload the profile picture to Firebase Storage
                blob.upload_from_file(profile_picture.file)
                blob.make_public()  # Make the file public
                
                # Get the public URL for the profile picture
                profile_picture_url = blob.public_url

            # Add preacher data to Firestore
            db.collection('preachers').add({
                'name': preacher_data['name'],
                'bio': preacher_data['bio'],
                'profile_picture_url': None,  # Add the profile picture URL
                'social_links': preacher_data.get('social_links', None),
                'created_at': firestore.SERVER_TIMESTAMP
            })

            messages.success(request, "Preacher has been added successfully")
            return redirect('categories')
        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, 'sermons/add_preacher_form.html', {'form': form})


# @login_required
# def createPlaylist(request):
#     form = PlaylistForm
#     if request.method == 'POST':
#         form = PlaylistForm(request.POST)
#         if form.is_valid():
#             messages.success(request, "Playlist has been created")
#             form.save()
#             return redirect('categories')
#     return render(request, 'sermons/add_playlist_form.html')


@login_required
def createPlaylist(request):
    form = PlaylistForm()
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist_data = form.cleaned_data

            # Add playlist data to Firestore
            db.collection('playlists').add({
                'name': playlist_data['name'],
                'description': playlist_data['description'],
                'created_at': firestore.SERVER_TIMESTAMP
            })

            messages.success(request, "Playlist has been created and stored in Firebase")
            return redirect('categories')
        else:
            messages.error(request, "Please correct the errors below.")

    return render(request, 'sermons/add_playlist_form.html', {'form': form})



# @login_required
# def createSermon(request):
#     form = SermonForm
#     preachers = Preacher.objects.all()
#     categories = Category.objects.all()
#     playlists = Playlist.objects.all()

#     context = {
#         'preachers': preachers,
#         'categories': categories,
#         'playlists': playlists,
#         'form' : form
#     }

#     if request.method == 'POST':
#         form = SermonForm(request.POST, request.FILES)
#         if form.is_valid():
#             messages.success(request, "Sermon has been created")
#             form.save()
#             return redirect('home')
#         else:
#             print("Form errors:")
#             for field, errors in form.errors.items():
#                 print(f"{field}: {errors}")
    
#     return render(request, 'sermons/add_sermons_form.html', context)



# @login_required
# def createSermon(request):
#     form = SermonForm
#     preachers = Preacher.objects.all()
#     categories = Category.objects.all()
#     playlists = Playlist.objects.all()

#     context = {
#         'preachers': preachers,
#         'categories': categories,
#         'playlists': playlists,
#         'form': form
#     }

#     if request.method == 'POST':
#         form = SermonForm(request.POST, request.FILES)
#         if form.is_valid():
#             # Initialize Firebase Storage
#             storage_client = storage.Client()
#             # bucket = storage_client.bucket('')  # Replace with your bucket name

#             # Handle audio file upload
#             audio_file = request.FILES.get('audio_file')
#             audio_file_url = None

#             if audio_file:
#                 try:
#                     unique_audio_filename = f"sermons/audio/{uuid.uuid4().hex}_{audio_file.name}"
#                     audio_blob = bucket.blob(unique_audio_filename)
#                     audio_blob.upload_from_file(audio_file.file)
#                     audio_blob.make_public()
#                     audio_file_url = audio_blob.public_url
#                 except Exception as e:
#                     print(f"Error uploading audio file: {e}")
#                     messages.error(request, "Failed to upload the audio file. Please try again.")
#                     return render(request, 'sermons/add_sermons_form.html', context)

#             # Handle image upload
#             image_file = request.FILES.get('image_file')
#             image_file_url = None

#             if image_file:
#                 try:
#                     unique_image_filename = f"sermons/images/{uuid.uuid4().hex}_{image_file.name}"
#                     image_blob = bucket.blob(unique_image_filename)
#                     image_blob.upload_from_file(image_file.file)
#                     image_blob.make_public()
#                     image_file_url = image_blob.public_url
#                 except Exception as e:
#                     print(f"Error uploading image file: {e}")
#                     messages.error(request, "Failed to upload the image file. Please try again.")
#                     return render(request, 'sermons/add_sermons_form.html', context)

#             # Save the sermon data
#             sermon = form.save(commit=False)
#             sermon.audio_file = audio_file_url  # Save audio file URL
#             sermon.image_file = image_file_url  # Save image file URL
#             sermon.save()
#             form.save_m2m()  # Save many-to-many relationships
#             messages.success(request, "Sermon has been created successfully")
#             return redirect('home')
#         else:
#             print("Form errors:")
#             for field, errors in form.errors.items():
#                 print(f"{field}: {errors}")

#     return render(request, 'sermons/add_sermons_form.html', context)


@login_required
def createSermon(request):
    # Fetch Firestore data for preachers, categories, and playlists
    preachers_ref = db.collection('preachers')
    preachers = preachers_ref.stream()
    preacher_list = [{**preacher.to_dict(), 'id': preacher.id} for preacher in preachers]

    categories_ref = db.collection('categories')
    categories = categories_ref.stream()
    category_list = [{**category.to_dict(), 'id': category.id} for category in categories]

    playlists_ref = db.collection('playlists')
    playlists = playlists_ref.stream()
    playlist_list = [{**playlist.to_dict(), 'id': playlist.id} for playlist in playlists]

    form = SermonForm(preachers=preacher_list, categories=category_list, playlists=playlist_list)

    if request.method == 'POST':
        form = SermonForm(
            request.POST,
            request.FILES,
            preachers=preacher_list,
            categories=category_list,
            playlists=playlist_list,
        )
        if form.is_valid():
            # Retrieve IDs from the form
            preacher_id = form.cleaned_data['preacher']
            category_id = form.cleaned_data['category']
            playlist_ids = form.cleaned_data['playlists']

            # Fetch the actual Firestore documents
            preacher_ref = db.collection('preachers').document(preacher_id)
            preacher = preacher_ref.get().to_dict()
            category_ref = db.collection('categories').document(category_id)
            category = category_ref.get().to_dict()
            playlists = []
            for playlist_id in playlist_ids:
                playlist_ref = db.collection('playlists').document(playlist_id)
                playlist = playlist_ref.get().to_dict()
                playlists.append(playlist)

            # Prepare the sermon data
            sermon_data = {
                'preacher': preacher.get('name', 'Unknown'),
                'category': category.get('name', 'Unknown'),
                'playlist': [playlist.get('name', 'Unknown') for playlist in playlists],
                'title': form.cleaned_data['title'],
                'description': form.cleaned_data['description'],
                'duration': str(form.cleaned_data['duration']),
                'date_published': form.cleaned_data['date_published'].isoformat(),
                'topic': form.cleaned_data['topic'],
                'tags': form.cleaned_data['tags'],
                'language': form.cleaned_data['language'],
                'play_count': form.cleaned_data['play_count'],
                'likes_count': form.cleaned_data['likes_count'],
                'created_at': firestore.SERVER_TIMESTAMP,
            }

            # Save to Firestore
            try:
                sermons_ref = db.collection('sermons')
                sermons_ref.add(sermon_data)
                messages.success(request, "Sermon has been created successfully.")
                return redirect('home')
            except Exception as e:
                print(f"Error saving sermon to Firestore: {e}")
                messages.error(request, "Failed to create the sermon. Please try again.")

        else:
            print("Form validation errors:", form.errors)

    context = {
        'preachers': preacher_list,
        'categories': category_list,
        'playlists': playlist_list,
        'form': form,
    }
    return render(request, 'sermons/add_sermons_form.html', context)




# @login_required(login_url='/login')
# def editCategory(request, pk):
#     category = Category.objects.get(id=pk)
#     context = {
#         'category': category
#     }

#     if request.method == 'POST':
#         form = CategoryForm(request.POST, instance=category)
#         if form.is_valid():
#             messages.success(request, "Category has been edited")
#             form.save()
#             return redirect('categories')
#     return render(request, 'sermons/edit_category.html', context)


# @login_required(login_url='/login')
# def deleteCategory(request, pk):
#     category = Category.objects.get(id=pk)
#     context = {
#         'category': category
#     }
#     if request.method == 'POST':
#         category.delete()
#         messages.success(request, "Category has been deleted")
#         return redirect('categories')
#     return render(request, 'sermons/delete_category.html', context)



@login_required(login_url='/login')
def editCategory(request, pk):
    # Fetch category from Firestore using the document ID (pk)
    category_ref = db.collection('categories').document(pk)
    category = category_ref.get()
    
    if not category.exists:
        messages.error(request, "Category not found.")
        return redirect('categories')

    category_data = category.to_dict()

    # If the method is POST, handle form submission
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        # Update the category in Firebase Firestore
        category_ref.update({
            'name': name,
            'description': description
        })

        messages.success(request, "Category has been edited")
        return redirect('categories')

    context = {
        'category': category_data
    }
    return render(request, 'sermons/edit_category.html', context)


@login_required(login_url='/login')
def deleteCategory(request, pk):
    # Fetch the category document from Firestore
    category_ref = db.collection('categories').document(pk)
    category = category_ref.get()

    if not category.exists:
        messages.error(request, "Category not found.")
        return redirect('categories')

    category_data = category.to_dict()

    if request.method == 'POST':
        # Delete the category from Firestore
        category_ref.delete()
        messages.success(request, "Category has been deleted")
        return redirect('categories')

    context = {
        'category': category_data
    }
    return render(request, 'sermons/delete_category.html', context)



# @login_required
# def editPreacher(request, pk):
#     preacher = Preacher.objects.get(id=pk)
#     context = {
#         'preacher' : preacher,
#     }

#     if request.method == "POST":
#         form = CategoryForm(request.POST, instance=preacher)
#         if form.is_valid():
#             messages.success(request, "Preacher has been edited successfully")
#             form.save()
#             return redirect("categories")
        
#     return render(request, "sermons/edit_preacher.html", context)


# @login_required(login_url='/login')
# def deletePreacher(request, pk):
#     preacher = Preacher.objects.get(id=pk)
#     context = {
#         'preacher': preacher
#     }
#     if request.method == 'POST':
#         preacher.delete()
#         messages.success(request, "Preacher has been deleted")
#         return redirect('categories')
#     return render(request, 'sermons/delete_preacher.html', context)


# @login_required
# def editPlaylist(request, pk):
#     playlist = Playlist.objects.get(id=pk)
#     context = {
#         'playlist' : playlist,
#     }

#     if request.method == "POST":
#         form = PlaylistForm(request.POST, instance=playlist)
#         if form.is_valid():
#             messages.success(request, "Playlist has been edited successfully")
#             form.save()
#             return redirect("categories")
        
#     return render(request, "sermons/edit_playlist.html", context)


# @login_required(login_url='/login')
# def deletePlaylist(request, pk):
#     playlist = Playlist.objects.get(id=pk)
#     context = {
#         'playlist': playlist
#     }
#     if request.method == 'POST':
#         playlist.delete()
#         messages.success(request, "Playlist has been deleted")
#         return redirect('categories')
#     return render(request, 'sermons/delete_playlist.html', context)



@login_required(login_url='/login')
def editPreacher(request, pk):
    # Fetch preacher from Firestore using the document ID (pk)
    preacher_ref = db.collection('preachers').document(pk)
    preacher = preacher_ref.get()
    
    if not preacher.exists:
        messages.error(request, "Preacher not found.")
        return redirect('categories')

    preacher_data = preacher.to_dict()

    # If the method is POST, handle form submission
    if request.method == 'POST':
        name = request.POST.get('name')
        bio = request.POST.get('bio')

        # Update the preacher in Firebase Firestore
        preacher_ref.update({
            'name': name,
            'bio': bio
        })

        messages.success(request, "Preacher has been edited successfully")
        return redirect('categories')

    context = {
        'preacher': preacher_data
    }
    return render(request, 'sermons/edit_preacher.html', context)



@login_required(login_url='/login')
def deletePreacher(request, pk):
    # Fetch the preacher document from Firestore
    preacher_ref = db.collection('preachers').document(pk)
    preacher = preacher_ref.get()

    if not preacher.exists:
        messages.error(request, "Preacher not found.")
        return redirect('categories')

    preacher_data = preacher.to_dict()

    if request.method == 'POST':
        # Delete the preacher from Firestore
        preacher_ref.delete()
        messages.success(request, "Preacher has been deleted")
        return redirect('categories')

    context = {
        'preacher': preacher_data
    }
    return render(request, 'sermons/delete_preacher.html', context)



@login_required(login_url='/login')
def editPlaylist(request, pk):
    # Fetch playlist from Firestore using the document ID (pk)
    playlist_ref = db.collection('playlists').document(pk)
    playlist = playlist_ref.get()
    
    if not playlist.exists:
        messages.error(request, "Playlist not found.")
        return redirect('categories')

    playlist_data = playlist.to_dict()

    # If the method is POST, handle form submission
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')

        # Update the playlist in Firebase Firestore
        playlist_ref.update({
            'name': name,
            'description': description
        })

        messages.success(request, "Playlist has been edited successfully")
        return redirect('categories')

    context = {
        'playlist': playlist_data
    }
    return render(request, 'sermons/edit_playlist.html', context)


@login_required(login_url='/login')
def deletePlaylist(request, pk):
    # Fetch the playlist document from Firestore
    playlist_ref = db.collection('playlists').document(pk)
    playlist = playlist_ref.get()

    if not playlist.exists:
        messages.error(request, "Playlist not found.")
        return redirect('categories')

    playlist_data = playlist.to_dict()

    if request.method == 'POST':
        # Delete the playlist from Firestore
        playlist_ref.delete()
        messages.success(request, "Playlist has been deleted")
        return redirect('categories')

    context = {
        'playlist': playlist_data
    }
    return render(request, 'sermons/delete_playlist.html', context)





# @login_required
# def editSermon(request, pk):
#     sermon = Sermon.objects.get(id=pk)
#     preachers = Preacher.objects.all()
#     categories = Category.objects.all()
#     playlists = Playlist.objects.all()

#     if request.method == "POST":
#         form = SermonForm(request.POST, request.FILES, instance=sermon)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Sermon has been edited successfully")
#             return redirect("home")
#         else:
#             print("Form errors:", form.errors)  # Debugging form errors
#     else:
#         form = SermonForm(instance=sermon)

#     context = {
#         'sermon': sermon,
#         'preachers': preachers,
#         'categories': categories,
#         'playlists': playlists,
#         'form': form,
#     }

#     return render(request, "sermons/edit_sermons.html", context)



# @login_required(login_url='/login')
# def deleteSermon(request, pk):
#     sermon = Sermon.objects.get(id=pk)
#     context = {
#         'sermon': sermon
#     }
#     if request.method == 'POST':
#         sermon.delete()
#         messages.success(request, "Sermon has been deleted")
#         return redirect('home')
#     return render(request, 'sermons/delete_sermons.html', context)




@login_required
def editSermon(request, pk):
    try:
        # Retrieve the sermon from Firestore
        sermon_ref = db.collection('sermons').document(pk)
        sermon_doc = sermon_ref.get()

        if not sermon_doc.exists:
            messages.error(request, "Sermon not found.")
            return redirect("home")

        sermon = sermon_doc.to_dict()

        # Fetch data for form dropdowns
        preachers_ref = db.collection('preachers').stream()
        categories_ref = db.collection('categories').stream()
        playlists_ref = db.collection('playlists').stream()

        preachers = [{**doc.to_dict(), 'id': doc.id} for doc in preachers_ref]
        categories = [{**doc.to_dict(), 'id': doc.id} for doc in categories_ref]
        playlists = [{**doc.to_dict(), 'id': doc.id} for doc in playlists_ref]

        if request.method == "POST":
            # Populate form with POST data
            form = SermonForm(request.POST, request.FILES, initial=sermon, preachers=preachers, categories=categories, playlists=playlists)

            if form.is_valid():
                # Update sermon data in Firestore
                updated_sermon = form.cleaned_data
                sermon_data = {
                    'title': updated_sermon['title'],
                    'description': updated_sermon['description'],
                    'preacher': updated_sermon['preacher'],
                    'category': updated_sermon['category'],
                    'playlist': updated_sermon['playlists'],  # Assuming playlists is a list
                    'duration': str(updated_sermon['duration']),
                    'date_published': updated_sermon['date_published'].isoformat(),
                    'topic': updated_sermon['topic'],
                    'tags': updated_sermon['tags'],
                    'language': updated_sermon['language'],
                    'play_count': updated_sermon['play_count'],
                    'likes_count': updated_sermon['likes_count'],
                }
                sermon_ref.update(sermon_data)  # Update Firestore document

                messages.success(request, "Sermon has been updated successfully.")
                return redirect("home")
            else:
                print("Form errors:", form.errors)  # Debugging form errors

        else:
            # Prepopulate the form with existing sermon data
            form = SermonForm(initial=sermon, preachers=preachers, categories=categories, playlists=playlists)

        context = {
            'sermon': sermon,
            'form': form,
            'preachers': preachers,
            'categories': categories,
            'playlists': playlists,
        }
        return render(request, "sermons/edit_sermons.html", context)

    except Exception as e:
        print(f"Error editing sermon: {e}")
        messages.error(request, "An error occurred while editing the sermon.")
        return redirect("home")


@login_required
def deleteSermon(request, pk):
    try:
        # Retrieve the sermon from Firestore
        sermon_ref = db.collection('sermons').document(pk)
        sermon_doc = sermon_ref.get()

        if not sermon_doc.exists:
            messages.error(request, "Sermon not found.")
            return redirect("home")

        if request.method == 'POST':
            # Delete sermon from Firestore
            sermon_ref.delete()
            messages.success(request, "Sermon has been deleted successfully.")
            return redirect("home")

        # Pass sermon details to the template
        context = {'sermon': sermon_doc.to_dict(), 'sermon_id': pk}
        return render(request, 'sermons/delete_sermons.html', context)

    except Exception as e:
        print(f"Error deleting sermon: {e}")
        messages.error(request, "An error occurred while deleting the sermon.")
        return redirect("home")
    


##################################################################
#EVENTS & DEVOTIONALS
#################################################################



# @login_required
# def events(request):
#     events = Events.objects.all()
#     devotionals = Devotion.objects.all()
#     context = {
#         'events': events,
#         'devotionals': devotionals
#     }
#     return render(request, 'events/events.html', context)

# @login_required
# def createDevotional(request):
#     form = DevotionForm()

#     if request.method == 'POST':
#         form = DevotionForm(request.POST, request.FILES)
#         if form.is_valid():
#             messages.success(request, "Devotional has been created")
#             form.save()
#             return redirect('events')
#         else:
#             for field, errors in form.errors.items():
#                 print(f"{field}: {errors}")

#     return render(request, 'events/add_devotional_form.html')

# @login_required
# def createEvent(request):
#     form = EventsForm()

#     if request.method == 'POST':
#         form = EventsForm(request.POST, request.FILES)
#         if form.is_valid():
#             messages.success(request, "Event has been created")
#             form.save()
#             return redirect('events')
#         else:
#             for field, errors in form.errors.items():
#                 print(f"{field}: {errors}") 

#     return render(request, 'events/add_event_form.html')


# @login_required(login_url='/login')
# def editDevotional(request, pk):
#     devotional = Devotion.objects.get(id=pk)
#     form = DevotionForm(instance=devotional)

#     if request.method == 'POST':
#         form = DevotionForm(request.POST, request.FILES, instance=devotional)
#         if form.is_valid():
#             messages.success(request, "Devotional has been edited")
#             form.save()
#             return redirect('devotionals')

#     context = {'form': form, 'devotional': devotional}
#     return render(request, 'events/edit_devotional_form.html', context)

# @login_required(login_url='/login')
# def editEvent(request, pk):
#     event = Events.objects.get(id=pk)
#     form = EventsForm(instance=event)

#     if request.method == 'POST':
#         form = EventsForm(request.POST, request.FILES, instance=event)
#         if form.is_valid():
#             messages.success(request, "Event has been edited")
#             form.save()
#             return redirect('events')

#     context = {'form': form, 'event': event}
#     return render(request, 'events/edit_event_form.html', context)


# @login_required(login_url='/login')
# def deleteDevotional(request, pk):
#     devotional = Devotion.objects.get(id=pk)

#     if request.method == 'POST':
#         devotional.delete()
#         messages.success(request, "Devotional has been deleted")
#         return redirect('events')

#     context = {'devotional': devotional}
#     return render(request, 'events/delete_devotional_form.html', context)
# @login_required(login_url='/login')


# def deleteEvent(request, pk):
#     event = Events.objects.get(id=pk)

#     if request.method == 'POST':
#         event.delete()
#         messages.success(request, "Event has been deleted")
#         return redirect('events')

#     context = {'event': event}
#     return render(request, 'events/delete_event_form.html', context)



@login_required
def events(request):
    try:
        events_ref = db.collection('events')
        event_docs = events_ref.stream()
        events = []
        for doc in event_docs:
            event_data = doc.to_dict()
            event_data['id'] = doc.id
            events.append(event_data)

        devotionals_ref = db.collection('devotionals')
        devotional_docs = devotionals_ref.stream()
        devotionals = []
        for doc in devotional_docs:
            devotional_data = doc.to_dict()
            devotional_data['id'] = doc.id
            devotionals.append(devotional_data)

        context = {
            'events': events,
            'devotionals': devotionals,
        }
        return render(request, 'events/events.html', context)
    except Exception as e:
        print(f"Error fetching events or devotionals: {e}")
        messages.error(request, "Failed to fetch events or devotionals.")
        return render(request, 'events/events.html', {})



@login_required
def createDevotional(request):
    form = DevotionForm()
    if request.method == 'POST':
        form = DevotionForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data

            # Convert any datetime.date to datetime.datetime if necessary
            for field, value in data.items():
                if isinstance(value, date):
                    data[field] = datetime.combine(value, datetime.min.time())

            # Handle the image file (upload to Firebase Storage) if needed
            # if 'devotional_thumbnail' in request.FILES:
            #     image_file = request.FILES['devotional_thumbnail']
            #     bucket = storage.bucket()
            #     blob = bucket.blob(f'devotionals/{image_file.name}')

            #     # Upload the image to Firebase Storage
            #     blob.upload_from_file(image_file, content_type=image_file.content_type)

            #     # Get the URL of the uploaded image
            #     image_url = blob.public_url

            #     # Add the URL to the data
            #     data['devotional_thumbnail'] = image_url
            # else:
            #     # If no image is provided, set it to None (or some default value)
            data['devotion_thumbnail'] = None

            # Save the devotional to Firestore
            devotional_ref = db.collection('devotionals').add(data)
            messages.success(request, "Devotional has been created")
            return redirect('events')  # Adjust the redirect to the correct URL
        else:
            for field, errors in form.errors.items():
                print(f"{field}: {errors}")

    return render(request, 'events/add_devotional_form.html')

@login_required
def createEvent(request):
    form = EventsForm()
    if request.method == 'POST':
        form = EventsForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data

            # Convert any datetime.date to datetime.datetime
            for field, value in data.items():
                if isinstance(value, date):
                    data[field] = datetime.combine(value, datetime.min.time())

            # Handle the image file (upload to Firebase Storage)
            # if 'event_thumbnail' in request.FILES:
            #     image_file = request.FILES['event_thumbnail']
            #     bucket = storage.bucket()
            #     blob = bucket.blob(f'events/{image_file.name}')

            #     # Upload the image to Firebase Storage
            #     blob.upload_from_file(image_file, content_type=image_file.content_type)

            #     # Get the URL of the uploaded image
            #     image_url = blob.public_url

            #     # Add the URL to the data
            data['event_thumbnail'] = None

            # Save event to Firebase
            event_ref = db.collection('events').add(data)
            messages.success(request, "Event has been created")
            return redirect('events')
        else:
            for field, errors in form.errors.items():
                print(f"{field}: {errors}")

    return render(request, 'events/add_event_form.html')


@login_required(login_url='/login')
def editDevotional(request, pk):
    try:
        devotional_ref = db.collection('devotionals').document(pk)
        devotional = devotional_ref.get()
        if not devotional.exists:
            messages.error(request, "Devotional not found.")
            return redirect('events')
        
        if request.method == 'POST':
            form = DevotionForm(request.POST, request.FILES)
            if form.is_valid():
                updated_data = form.cleaned_data
                # Update devotional in Firebase
                devotional_ref.update(updated_data)
                messages.success(request, "Devotional has been edited")
                return redirect('events')
            else:
                for field, errors in form.errors.items():
                    print(f"{field}: {errors}")
        else:
            # Use initial for pre-filling form
            form = DevotionForm(initial=devotional.to_dict())

        context = {'form': form, 'devotional': devotional.to_dict()}
        return render(request, 'events/edit_devotional_form.html', context)


    except Exception as e:
        print(f"Error editing devotional: {e}")
        messages.error(request, "Error editing devotional.")
        return redirect('events')



@login_required(login_url='/login')
def editEvent(request, pk):
    try:
        event_ref = db.collection('events').document(pk)
        event = event_ref.get()
        if not event.exists:
            messages.error(request, "Event not found.")
            return redirect('events')

        if request.method == 'POST':
            form = EventsForm(request.POST, request.FILES)
            if form.is_valid():
                updated_data = form.cleaned_data

                # Convert date fields to datetime
                for key, value in updated_data.items():
                    if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
                        updated_data[key] = datetime.combine(value, datetime.min.time())

                # Update event in Firebase
                event_ref.update(updated_data)
                messages.success(request, "Event has been edited")
                return redirect('events')
            else:
                for field, errors in form.errors.items():
                    print(f"{field}: {errors}")
        else:
            form = EventsForm(initial=event.to_dict())

        context = {'form': form, 'event': event.to_dict()}
        return render(request, 'events/edit_event_form.html', context)

    except Exception as e:
        # Use traceback to log the stack trace
        print(f"Error editing event: {e}")
        traceback.print_exc()
        messages.error(request, "Error editing event.")
        return redirect('events')


@login_required(login_url='/login')
def editEvent(request, pk):
    try:
        event_ref = db.collection('events').document(pk)
        event = event_ref.get()
        if not event.exists:
            messages.error(request, "Event not found.")
            return redirect('events')

        if request.method == 'POST':
            form = EventsForm(request.POST, request.FILES)
            if form.is_valid():
                updated_data = form.cleaned_data

                # Convert date fields to datetime
                for key, value in updated_data.items():
                    if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
                        updated_data[key] = datetime.combine(value, datetime.min.time())

                # Update event in Firebase
                event_ref.update(updated_data)
                messages.success(request, "Event has been edited")
                return redirect('events')
            else:
                for field, errors in form.errors.items():
                    print(f"{field}: {errors}")
        else:
            form = EventsForm(initial=event.to_dict())

        context = {'form': form, 'event': event.to_dict()}
        return render(request, 'events/edit_event_form.html', context)

    except Exception as e:
        messages.error(request, "Error editing event.")
        return redirect('events')



@login_required(login_url='/login')
def deleteDevotional(request, pk):
    try:
        devotional_ref = db.collection('devotionals').document(pk)
        devotional = devotional_ref.get()
        if not devotional.exists:
            messages.error(request, "Devotional not found.")
            return redirect('events')

        if request.method == 'POST':
            devotional_ref.delete()
            messages.success(request, "Devotional has been deleted")
            return redirect('events')

        context = {'devotional': devotional.to_dict()}
        return render(request, 'events/delete_devotional_form.html', context)

    except Exception as e:
        print(f"Error deleting devotional: {e}")
        messages.error(request, "Error deleting devotional.")
        return redirect('events')

@login_required(login_url='/login')
def deleteEvent(request, pk):
    try:
        event_ref = db.collection('events').document(pk)
        event = event_ref.get()
        if not event.exists:
            messages.error(request, "Event not found.")
            return redirect('events')

        if request.method == 'POST':
            event_ref.delete()
            messages.success(request, "Event has been deleted")
            return redirect('events')

        context = {'event': event.to_dict()}
        return render(request, 'events/delete_event_form.html', context)

    except Exception as e:
        print(f"Error deleting event: {e}")
        messages.error(request, "Error deleting event.")
        return redirect('events')




########################################################
# Api Views
########################################################

# class SermonListView(APIView):
#     def get(self, request):
#         sermons = Sermon.objects.all()
#         serializer = SermonSerializer(sermons, many=True, context={'request': request})
#         return Response(serializer.data)

# class DevotionalListView(APIView):
#     def get(self, request):
#         devotions = Devotion.objects.all()
#         serializer = DevotionalsSerializer(devotions, many=True, context={'request': request})
#         return Response(serializer.data)

# class EventsListView(APIView):
#     def get(self, request):
#         events = Events.objects.all()
#         serializer = EventsSerializer(events, many=True, context={'request': request})
#         return Response(serializer.data)

# class CategoryListView(APIView):
#     def get(self, request):
#         category = Category.objects.all()
#         serializer = CategorySerializer(category, many=True, context={'request': request})
#         return Response(serializer.data)


class SermonListView(APIView):
    def get(self, request):
        sermons_ref = db.collection('sermons')
        sermons = [doc.to_dict() for doc in sermons_ref.stream()]
        for sermon in sermons:
            sermon['bg_picture_url'] = request.build_absolute_uri(sermon['bg_picture']) if 'bg_picture' in sermon else None
            sermon['audio_file_url'] = request.build_absolute_uri(sermon['audio_file']) if 'audio_file' in sermon else None
        return Response(sermons)


class DevotionalListView(APIView):
    def get(self, request):
        devotions_ref = db.collection('devotionals')
        devotions = [doc.to_dict() for doc in devotions_ref.stream()]
        for devotion in devotions:
            devotion['devotion_thumbnail_url'] = request.build_absolute_uri(devotion['devotion_thumbnail']) if 'devotion_thumbnail' in devotion else None
        return Response(devotions)


class EventsListView(APIView):
    def get(self, request):
        events_ref = db.collection('events')
        events = [doc.to_dict() for doc in events_ref.stream()]
        for event in events:
            event['event_thumbnail_url'] = request.build_absolute_uri(event['event_thumbnail']) if 'event_thumbnail' in event else None
        return Response(events)


class CategoryListView(APIView):
    def get(self, request):
        categories_ref = db.collection('categories')
        categories = [doc.to_dict() for doc in categories_ref.stream()]
        for category in categories:
            category['category_thumbnail_url'] = request.build_absolute_uri(category['category_thumbnail']) if 'category_thumbnail' in category else None
        return Response(categories)
    
class PreacherListView(APIView):
    def get(self, request):
        preachers_ref = db.collection('preachers')
        preachers = [doc.to_dict() for doc in preachers_ref.stream()]
        for preacher in preachers:
            preacher['profile_picture_url'] = request.build_absolute_uri(preacher['profile_picture']) if 'profile_picture' in preacher else None
        return Response(preachers)


class PlaylistListView(APIView):
    def get(self, request):
        playlists_ref = db.collection('playlists')
        playlists = [doc.to_dict() for doc in playlists_ref.stream()]
        return Response(playlists)




#########################################
# End of API views
#########################################




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

