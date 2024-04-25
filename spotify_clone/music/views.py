from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
import requests
# Create your views here.
def top_artists():
    url = "https://65d16bd9ab7beba3d5e455e6.mockapi.io/todolist/artists"
    response = requests.get(url)
    response_data = response.json()
    artists_info = []

    for artist in response_data:
        name = artist.get('nameArtist', 'No Name')
        idArtist = artist.get('idArtist', 'No ID')
        imageArtist = artist.get('imageArtist', 'No Image')
        artists_info.append((name,idArtist,imageArtist))
    return artists_info

def top_tracks():
    url = "https://66160055b8b8e32ffc7c19db.mockapi.io/toptracks"
    response = requests.get(url)
    response_data = response.json()
    track_details=[]

    for track in response_data:
        track_id = track['track_id']
        track_name = track['track_name']
        artist_name = track['artist_name']
        cover_url = track['cover_url']

        track_details.append({
            'track_id':track_id,
            'track_name':track_name,
            'artist_name':artist_name,
            'cover_url':cover_url
        })
    return track_details

def get_audio_details(query):
    url = "https://spotify-scraper.p.rapidapi.com/v1/track/download"
    querystring = {"track":query}

    headers = {
        "X-RapidAPI-Key": "d01f11a307mshf1c4745d6bd7c6fp1d217fjsn80edc9228357",
            "X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    audio_details = []

    if response.status_code == 200:
        data = response.json()
        if 'youtubeVideo' in data and 'audio' in data['youtubeVideo'] and 'spotifyTrack' in data and 'album' in data['spotifyTrack']:
            audio_list = data['youtubeVideo']['audio']
            cover_url = data['spotifyTrack']['album']['cover']
            if audio_list and cover_url:
                first_audio_url = audio_list[0]['url']
                duration_text = audio_list[0]['durationText']
                image_url = cover_url[0]['url']
                first_audio_url = audio_list[0]['url']
                audio_details.append(first_audio_url)
                audio_details.append(duration_text)
                audio_details.append(image_url)
            else:
                print("No Audio or Image Avaliable")
        else:
            print("No 'youtubeVideo' or 'SpotifyTrack' found")
    else:
        print('Failed to fetch data')
    return audio_details

@login_required(login_url='login')
def music(request,pk):
    track_id = pk
    url = "https://spotify-scraper.p.rapidapi.com/v1/track/metadata"
    querystring = {"trackId":track_id}
    headers = {
         "X-RapidAPI-Key": "d01f11a307mshf1c4745d6bd7c6fp1d217fjsn80edc9228357",
            "X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = response.json()
        track_name = data.get("name")
        artists_list = data.get("artists",[])
        first_artist_name = artists_list[0].get('name') if artists_list else "No artist found"
        audio_details_query=track_name + first_artist_name
        audio_details = get_audio_details(audio_details_query)
        audio_url= audio_details[0]
        duration_text = audio_details[1]
        image_url = audio_details[2]
        context ={
            'track_name':track_name,
            'artist_name':first_artist_name,
            'audio_url':audio_url,
            'duration_text':duration_text,
            'image_url':image_url,
        }    
    return render(request,'music.html',context) 

@login_required(login_url='login')
def profile(request,pk):
    artist_id = pk
    url = "https://spotify-scraper.p.rapidapi.com/v1/artist/overview"
    querystring = {"artistId":artist_id}
    headers = {
			 "X-RapidAPI-Key": "d01f11a307mshf1c4745d6bd7c6fp1d217fjsn80edc9228357",
            "X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
	}
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = response.json()

        name = data['name']
        monthly_listeners = int(data['stats']['monthlyListeners'])
        formatMonthlyListeners = f'{monthly_listeners:,}'
        header_url = data['visuals']['header'][0]['url']
        top_tracks =[]
        for track in data['discography']['topTracks']:
            trackId = str(track['id'])
            trackName = str(track['name'])
            trackImage = str(track['album']['cover'][0]['url'])
            formatPlayCount = f'{track['playCount']:,}'
            track_info ={
                "id":trackId,
                "name":trackName,
                "track_image":trackImage,
                "durationText":track['durationText'],
                "playCount":formatPlayCount
            }
            top_tracks.append(track_info)

        artist_data ={
            'name':name,            
            'monthly_listeners':formatMonthlyListeners,            
            'header_url':header_url,     
            'top_tracks': top_tracks      
        }
    else:
        artist_data={}
    return render(request,'profile.html',artist_data)

@login_required(login_url='login')
def search(request):
    if request.method == 'POST':
        seach_query = request.POST['search_query']
        url = "https://spotify-scraper.p.rapidapi.com/v1/search"

        querystring = {"term":seach_query,"type":"track"}

        headers = {
            "X-RapidAPI-Key": "d01f11a307mshf1c4745d6bd7c6fp1d217fjsn80edc9228357",
            "X-RapidAPI-Host": "spotify-scraper.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        track_list =[]
        if response.status_code == 200:
            data = response.json()
            seach_result_count = data['tracks']['totalCount']
            tracks = data['tracks']['items']

            for track in tracks:
                track_name = track['name']
                artist_name = track['artists'][0]['name']
                duration = track['durationText']
                trackId = track['id']
                trackImage = track['album']['cover'][0]['url']

                track_list.append({
                    'track_name':track_name,
                    'artist_name':artist_name,
                    'duration':duration,
                    'trackId':trackId,
                    'trackImage':trackImage,
                })
            context ={
                'seach_result_count':seach_result_count,
                'track_list':track_list,
            }
        return render(request,'search.html',context)
    else:
        return render(request,'search.html')

@login_required(login_url='login')
def index(request):
    artists_info = top_artists()
    top_track_list = top_tracks()
    
    first_six_tracks = top_track_list[:6]
    second_six_tracks = top_track_list[6:12]
    third_six_tracks = top_track_list[12:18]
    context = {
        'artists_info': artists_info,
        'first_six_tracks': first_six_tracks,
        'second_six_tracks': second_six_tracks,
        'third_six_tracks': third_six_tracks,
    }
    return render(request,'index.html',context)

def login(request):
    if request.method =="POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request,user)
            return redirect('/')
        else:
            messages.info(request,'Credentials Invalid')
            return redirect('login')
    else:
        return render(request,'login.html')
    
def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request,'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request,'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username,email=email,password=password)
                user.save()

                # login user in
                user_login = auth.authenticate(username=username,password=password)
                auth.login(request,user_login)
                return redirect('/')
        else:
            messages.info(request,'Password not matching')
            return redirect('signup')
    else:
        return render(request,'signup.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')