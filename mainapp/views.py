from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login as auth_login
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
import random, spotipy, json, sys, pprint, os, time, numpy as np, pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
from .models import Artist,Album,Track,Profile,Rating
from django.http import HttpResponse, QueryDict
from datetime import datetime as dt
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import sigmoid_kernel
from datetime import datetime as dt
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages

@csrf_exempt
def search_page(request):
	context = {}

	if request.user.is_authenticated and request.method == "PUT":
		user = User.objects.get(id=int(request.user.pk))
		my_favourites = Track.objects.filter(favourites__id=request.user.pk)

		put = QueryDict(request.body)
		objective = put.get('objective')
		track_id = int(put.get('track_id'))
		track = Track.objects.get(id=track_id)

		if objective == "remove_from_favourites" and track in my_favourites:
			print("remove_from_favourites")
			user.favourites.remove(track)
			return HttpResponse(json.dumps({"status_code": 204, "status": "success"}), content_type="application/json")

		if objective == "add_to_favourites" and not track in my_favourites:
			print("add_to_favourites")
			user.favourites.add(track)
			return HttpResponse(json.dumps({"status_code": 204, "status": "success"}), content_type="application/json")

		return HttpResponse(json.dumps({"status_code": 204, "status": "failure"}), content_type="application/json")	

	if request.method == "POST" and 'musicsearch' in request.POST:
		# track_results = []
		query = request.POST['musicsearch']
		client_credentials_manager = SpotifyClientCredentials(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET)
		sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager) #spotify object to access API

		result = sp.search(query) #search query
		artist_name = result['tracks']['items'][0]['artists'][0]['name']
		artist_id = result['tracks']['items'][0]['artists'][0]['id']
		artist_uri = result['tracks']['items'][0]['artists'][0]['uri']

		# Adding the artist to the db.
		if Artist.objects.filter(artist_name=artist_name,artist_spotify_id=artist_id,artist_uri=artist_uri).exists():
			the_artist = Artist.objects.get(artist_spotify_id=artist_id,artist_uri=artist_uri)
		else:
			the_artist = Artist.objects.create(artist_name=artist_name,artist_spotify_id=artist_id,artist_uri=artist_uri)

		# Get all of the album that belongs to the searched artist
		sp_albums = sp.artist_albums(artist_uri, limit=1, album_type='album')

		# Adding all the albums associated to the Artist
		for i in range(len(sp_albums['items'])):
			album_name = sp_albums['items'][i]['name']
			album_uri = sp_albums['items'][i]['uri']
			spotify_id = sp_albums['items'][i]['id']
			album_image = sp_albums['items'][i]['id']

			
			if Album.objects.filter(artist=the_artist,album_name=album_name).exists():
				the_album = Album.objects.get(artist=the_artist,album_name=album_name)
			else:
				the_album = Album.objects.create(artist=the_artist,album_name=album_name,album_spotify_id=spotify_id,album_uri=album_uri)

			# Get all the tracks for each album and store it in the db
			tracks = sp.album_tracks(album_uri, limit=12) # pull data on album tracks

			for n in range(len(tracks['items'])): #for each song track
				track_name = tracks['items'][n]['name']
				track_id = tracks['items'][n]['id']
				track_uri = tracks['items'][n]['uri']
				track_image = result['tracks']['items'][0]["album"]["images"][0]["url"]
				features = sp.audio_features(track_uri)#In the future make bulk API request as track_url can be of type list of multiple track uri's.

				danceability = features[0]['danceability']
				energy = features[0]['energy']
				loudness = features[0]['loudness']
				speechiness = features[0]['speechiness']
				acousticness = features[0]['acousticness']
				instrumentalness = features[0]['instrumentalness']
				liveness = features[0]['liveness']
				valence = features[0]['valence']
				tempo = features[0]['tempo']

				if not Track.objects.filter(album=the_album,track_name=track_name).exists():
					the_track = Track.objects.create(album=the_album,artist=the_artist,track_name=track_name,
						track_id=track_id,track_uri=track_uri,track_image=track_image,
						danceability=danceability,energy=energy,loudness=loudness,speechiness=speechiness,
						acousticness=acousticness,instrumentalness=instrumentalness,liveness=liveness,
						valence=valence,tempo=tempo)
		track_results = Track.objects.filter(track_name__icontains=query) | Track.objects.filter(artist__artist_name__icontains=query) | Track.objects.filter(album__album_name__icontains=query)
		track_results = track_results[:10]
		track_results_2 = []
		if request.user.is_authenticated:
			for track in track_results:
				in_favourites = True if track in Track.objects.filter(favourites__id=request.user.pk) else False
				data = {"id": track.id, "track_name": track.track_name, "artist_name": track.artist.artist_name, "in_favourites": in_favourites}
				track_results_2.append(data)
			track_results = track_results_2
			context["track_results"] = track_results
			return render(request,'mainapp/search_page.html',context)
		context["track_results"] = track_results
	return render(request,"mainapp/search_page.html",context)

def sign_up(request):
	# DONE
	if request.method == "POST":
		first_name = request.POST['first_name']
		last_name = request.POST['last_name']
		email = request.POST['email']
		password = request.POST['password']
		password_2 = request.POST['password_2']
		tempo = float(request.POST['tempo'])
		speechiness = float(request.POST['speechiness'])
		energy = float(request.POST['energy'])

		if password and password_2:
			if password != password_2:
				return render(request,'mainapp/sign_up.html',{"message": "Password does not match."})

		if not User.objects.filter(email=email).exists():
			user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)
			user.is_active = False#Change this to false once done
			user.save()
			Profile.objects.create(user=user,tempo=tempo, speechiness=speechiness, energy=energy)
			current_site = get_current_site(request)

			email_subject = "Activate your MuserApp Account"
			message = render_to_string('mainapp/activate.html',
				{"user":user,
				"domain":current_site.domain,
				"uid": urlsafe_base64_encode(force_bytes(user.pk)),
				"token": generate_token.make_token(user)
				})

			email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [email])
			email_message.send()

			context = {"activate": "We've sent you an activation link. Please check your email."}
			return render(request,'mainapp/sign_up.html',context)

		else:
			return render(request,'mainapp/sign_up.html',{"message": "E-mail taken already"})

	return render(request,'mainapp/sign_up.html',{})

def login(request):
	# DONE
    if request.method == 'POST' and 'login' in request.POST:
    	print("login")
    	email = request.POST['email']
    	password = request.POST['password']
    	user = authenticate(username=email, password=password)
    	if user:
    		auth_login(request, user)
    		return redirect("mainapp:index")
    	else:
    		return render(request,'mainapp/login.html', {"message": "The username and password does not match, please try again"})
    return render(request,'mainapp/login.html', {})

def password_request(request):
	print("c0")
	if request.method == "POST":
		email = request.POST["email"]
		print("c1")

		try:
			user = User.objects.get(username=email)
		except User.DoesNotExist:
			user = None
		print("c2")

		if user is not None:
			print("c3")
			username = user.first_name

			current_site = get_current_site(request)
			domain = current_site.domain
			print("c4")

			uid = urlsafe_base64_encode(force_bytes(user.pk))
			token = generate_token.make_token(user)
			print("c5q")

			email_subject = "Request to change MuserApp Password"
			message = """Hi {},\n\n
			You have recently request to change your account password.
			Please click this link below to change your account password. \n\n
			http://{}/password_change/{}/{}""".format(username, domain, uid, token)
			print("email sent")

			email_message = EmailMessage(email_subject, message, settings.EMAIL_HOST_USER, [email])
			email_message.send()

		return render(request, "mainapp/password_request.html",{"message": "Check your email for a password change link."})
	return render(request, "mainapp/password_request.html",{})

# def profiles(request):
# 	if not request.user.is_authenticated:
# 		return redirect("mainapp:login")

# 	if request.method == 'POST':
# 		a_form = UserUpdateForm(request.POST, instance=request.user)
# 		f_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

# 		if a_form.is_valid() and  f_form.is_valid():
# 			a_form.save()
# 			f_form.save()
# 			messages.success(request, f'Account Updated')
# 			return redirect('profile')
# 		else:
# 			previous_image = os.path.join(settings.MEDIA_ROOT, request.user.profile.profilepic.name)
# 			a_form = UserUpdateForm(instance=request.user)
# 			f_form = ProfileUpdateForm(instance=request.user.profile)

# 		context = {
# 			'a_form': a_form,
# 			'f_form': f_form
# 		}
# 	#Delete Previous Image To Avoid Duplicated Images Of Same User.
# 	if previous_image != "default.jpg" and previous_image != os.path.join(settings.MEDIA_ROOT, request.user.profile.profilepic.name):
# 		os.remove(previous_image)
# 	return render(request, 'userapp/profile.html', context)


def profile(request):
	if not request.user.is_authenticated:
		return redirect("mainapp:login")

	context = {}
	user = User.objects.get(id=int(request.user.pk))
	profile = Profile.objects.get(user=request.user)

	if request.method == "POST":
		first_name = request.POST['first_name'].strip()
		last_name = request.POST['last_name'].strip()
		password = request.POST['password']
		tempo = float(request.POST['tempo'])
		speechiness = float(request.POST['speechiness'])
		energy = float(request.POST['energy'])

		user = User.objects.get(pk=(request.user.id))
		user.first_name = first_name
		user.last_name = last_name

		profile.tempo = tempo
		profile.speechiness = speechiness
		profile.energy = energy

		if password:
			password_change = True
			user.set_password(password)
		else:
			password_change = False

		# f_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

		# if f_form.is_valid():
		# 	f_form.save()
		# 	messages.success(request, f'Account Updated')
		# 	return redirect('mainapp:profile')

		user.save()
		profile.save()

		if password_change:
			user = authenticate(username=user.email, password=password)

			if user:
				auth_login(request, user)
			else:
				return redirect("mainapp:login")
	# else:
	# 	previous_image = os.path.join(settings.MEDIA_ROOT, request.user.profile.profilepic.name)
	# 	a_form = UserUpdateForm(instance=request.user)
	# 	f_form = ProfileUpdateForm(instance=request.user.profile)

	# context['f_form'] = f_form
	#Delete Previous Image To Avoid Duplicated Images Of Same User.
	# if previous_image != "default.jpg" and previous_image != os.path.join(settings.MEDIA_ROOT, request.user.profile.profilepic.name):
		# os.remove(previous_image)

	context["user"] = user
	context["profile"] = profile
	return render(request,'mainapp/profile.html',context)

def log_out(request):
	# DONE
	request.session.flush()
	logout(request)
	return redirect('mainapp:index')

@csrf_exempt
def index(request):
	return render(request,'mainapp/index.html',{})

@csrf_exempt
def library(request):
	if not request.user.is_authenticated:
		return redirect("mainapp:login")

	user = User.objects.get(id=int(request.user.pk))
	my_favourites = Track.objects.filter(favourites__id=request.user.pk)
	if request.method == "PUT":
		put = QueryDict(request.body)
		objective = put.get('objective')
		track_id = int(put.get('track_id'))
		track = Track.objects.get(id=track_id)

		if track in my_favourites:
			user.favourites.remove(track)
			return HttpResponse(json.dumps({"status_code": 204, "status": "success"}), content_type="application/json")

	my_favourites = Track.objects.filter(favourites__id=request.user.pk)

	my_recommendation = collaborative_filtering(request)
	w_average = weighted_average(request)
	default_recomendation = above_average(request)

	print({"my_recommendation":len(my_recommendation),"w_average":len(w_average),"default_recomendation":len(default_recomendation)})

	my_recommendation = my_recommendation+default_recomendation+w_average

	context = {"my_favourites": my_favourites, "my_recommendation":my_recommendation}
	return render(request,'mainapp/library.html',context)

def above_average(request):
	user = User.objects.get(id=int(request.user.pk))
	profile = Profile.objects.get(user=request.user)

	energy_range = [profile.energy*0.9, profile.energy*1.1]
	speechiness_range = [profile.speechiness*0.9, profile.speechiness*1.1]
	tempo_range = [profile.tempo*0.9, profile.tempo*1.1]


	result = Track.objects.filter(energy__gte=energy_range[0],energy__lte=energy_range[1]) | Track.objects.filter(speechiness__gte=speechiness_range[0],speechiness__lte=speechiness_range[1]) | Track.objects.filter(tempo__gte=tempo_range[0],tempo__lte=tempo_range[1])
	rating_filtered = []
	for tracks in result:
		# Calculating the average rating for the iterating track.
		total_rating = 0
		rating = Rating.objects.filter(track=tracks)
		for i in rating:
			total_rating+= i.rating_value

		try:
			average_rating = round(total_rating/rating.count(),2)
			rating_count = rating.count()
		except Exception as e:
			average_rating = 0.0
			rating_count = 0

		if average_rating>3.5:
			rating_filtered.append(tracks)
	return rating_filtered

def weighted_average(request):
	tracks_df = []
	for tracks in Track.objects.all():
		track_id = tracks.id
		album_name = tracks.album.album_name
		artist_name = tracks.artist.artist_name
		track_name = tracks.track_name
		energy = tracks.energy
		acousticness = tracks.acousticness
		tempo = tracks.tempo

		# Calculating the average rating for the iterating track.
		total_rating = 0
		rating = Rating.objects.filter(track=tracks)
		for i in rating:
			total_rating+= i.rating_value

		try:
			average_rating = round(total_rating/rating.count(),2)
			rating_count = rating.count()
		except Exception as e:
			average_rating = 0.0
			rating_count = 0

		tracks_df.append([track_id, album_name, artist_name, track_name, energy, acousticness, tempo, average_rating, rating_count])

	df = pd.DataFrame(data=tracks_df, columns=['track_id', 'album_name','artist_name','track_name','energy','acousticness','tempo', 'average_rating', 'rating_count'])

	V = df['rating_count']
	R = df['average_rating']
	C = df['average_rating'].mean()
	M = df['rating_count'].quantile(0.70)

	df['weighted_average'] = ((R*V) + (C*M))/(V+M)

	track_sorted_ranking = df.sort_values('weighted_average', ascending=False)
	track_sorted_ranking[['track_id', 'album_name','artist_name','track_name','energy','acousticness','tempo', 'average_rating', 'rating_count']]

	by_rating_count = track_sorted_ranking.sort_values('rating_count', ascending=False)

	scaling = MinMaxScaler()
	track_scaled = scaling.fit_transform(df[['weighted_average', 'rating_count']])
	track_normalized = pd.DataFrame(track_scaled, columns=['weighted_average', 'rating_count'])

	df[['normalized_weight_average','normalized_popularity']] = track_normalized
	df['score'] = df['normalized_weight_average'] * 0.5 + df['normalized_popularity'] * 0.5
	songs_scored_df = df.sort_values(['score'], ascending=False)
	final_result = songs_scored_df[['track_id', 'track_name', 'normalized_weight_average', 'normalized_popularity', 'score']].head(15)

	list_of_track_id = list(final_result['track_id'])
	list_of_tracks = []

	for track_ids in list_of_track_id:
		list_of_tracks.append(Track.objects.get(id=int(track_ids)))

	return list_of_tracks

def track_page(request, id):
	track = Track.objects.get(id=id)
	rating = Rating.objects.filter(track=track).order_by('-created_at')

	if request.method == "POST" and request.user.is_authenticated:
		if 'selected-rating' in request.POST:
			value = int(request.POST['selected-rating'])
			description = request.POST['description']
			if Rating.objects.filter(track=track, user=request.user).exists():
				Rating.objects.filter(track=track, user=request.user).delete()
				print("deleted")
			Rating.objects.create(track=track, user=request.user, rating_value=value, description=description, created_at=dt.now())

		user = User.objects.get(id=int(request.user.pk))
		my_favourites = Track.objects.filter(favourites__id=request.user.pk)

		if 'add_to_favourites' in request.POST and not track in my_favourites:
			user.favourites.add(track)

		if 'remove_from_favourites' in request.POST and track in my_favourites:
			user.favourites.remove(track)
	else:
		print("jksabdkj")
		# return redirect("mainapp:login")

	in_favourites = True if track in Track.objects.filter(favourites__id=request.user.pk) else False

	ratings_value = 0
	for i in rating:
		ratings_value+= i.rating_value
	try:
		average_rating = round(ratings_value/rating.count(),2)
	except Exception as e:
		average_rating = 0.0
	average_rating = int(round(average_rating))
	print("average_rating",average_rating)

	context = {"track": track, "rating":rating, "average_rating":average_rating, "in_favourites":in_favourites, "rating_count":rating.count()}
	return render(request,'mainapp/track_page.html',context)

def collaborative_filtering(request):
	user_ratings = [[r.user.email, r.rating_value, r.track.track_id] for r in Rating.objects.all()[:50]]
	rating_df = pd.DataFrame(data=user_ratings, columns=["the_user", "rating_value", "track_id"])
	
	track_details = [[t.track_id, t.track_name] for t in Track.objects.all()]
	track_df = pd.DataFrame(data=track_details, columns=["track_id", "track_name"])

	rating_df = pd.merge(track_df,rating_df)
	user_ratings = rating_df.pivot_table(index=['the_user'],columns=['track_name'],values='rating_value')
	correlation_matrix = user_ratings.corr(method='pearson')

	def get_similar(title,rating):
	    close_ratings = correlation_matrix[title]*(rating-2.5)
	    close_ratings = close_ratings.sort_values(ascending=False)
	    return close_ratings

	user_ratings = Rating.objects.filter(user=request.user).filter(rating_value=5).order_by('-rating_value')
	get_tracks = [(r.track.track_name, r.rating_value) for r in user_ratings]

	similar_tracks = pd.DataFrame()
	for title, rating in get_tracks:
		try:
			similar_tracks = similar_tracks.append(get_similar(title,rating),ignore_index = True)
		except:
			pass

	tracks_recommend= similar_tracks.sum().sort_values(ascending=False).head(10)
	top_tracks = [tracks_recommend[tracks_recommend==i].index[0] for i in tracks_recommend]
	top_track_objects = []
	for title in top_tracks:
		top_track_objects  = top_track_objects + list(Track.objects.filter(track_name__icontains=title.strip().lower()))
	sanitised_list = []
	added_names = []
	for i in top_track_objects:
		if i not in sanitised_list and i.track_name not in added_names:
			sanitised_list.append(i)
			added_names.append(i.track_name)
	return sanitised_list

def activateaccount(request, uidb64, token):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except Exception as e:
		user = None

	if user is not None and generate_token.check_token(user, token):
		user.is_active = True
		user.save()
		messages.add_message(request,messages.SUCCESS,"Account activated successfully")
		return redirect('mainapp:login')
	return render(request, "mainapp/activate_failed.html",status=401)



def password_change(request, uidb64, token):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except Exception as e:
		user = None

	if request.method == "POST" and user is not None and generate_token.check_token(user, token):
		password_1 = request.POST["password_1"]
		password_2 = request.POST["password_2"]

		if password_1 and password_2:
			if(password_1!=password_2):
				context = {"message": "Your passwords do not match!"}
				return render(request,"mainapp/password_reset_form.html", context)

			if(len(password_1)<8 or any(letter.isalpha() for letter in password_1)==False or any(capital.isupper() for capital in password_1)==False or any(number.isdigit() for number in password_1)==False):
				context = {"message": "Your password is not strong enough."}
				return render(request,"mainapp/password_reset_form.html", context)

			user.set_password(password_1)
			user.save()
			return redirect("mainapp:login")

	if user is not None and generate_token.check_token(user, token):
		return render(request, "mainapp/password_reset_form.html",{})
	else:
		return render(request, "mainapp/activate_failed.html",status=401)
