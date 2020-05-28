from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import path, include, reverse, resolve
from datetime import datetime as dt, date
from mainapp.models import Artist,Album,Track,Profile,Rating

# python manage.py test mainapp/tests

class AccountProfileTest(TestCase):
	def create_user(self, username, email, password, first_name, last_name):
		return User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)

	# def create_user_profile(self, user ,tempo, speechiness, energy):
	# 	return user.profile.create(tempo=tempo, speechiness=speechiness, energy=energy)

	def setUp(self):
		newuser = self.create_user("harry.potter@live.com", "harry.potter@live.com", "123Chirag123", "Harry", "Potter")
		# newprofile = self.create_user_profile(newuser, 0.0, 1.0, 0.5)

	def tearDown(self):
		User.objects.all().delete()

	def test_user_attributes(self):
		user = User.objects.get(email="harry.potter@live.com")
		self.assertEqual(user.username,"harry.potter@live.com")
		self.assertEqual(user.first_name,"Harry")
		self.assertEqual(user.last_name,"Potter")

	# def test_profile_attribute(self):
	# 	user = User.objects.get(email="harry.potter@live.com")
	# 	profile = Profile.objects.get(userid=user)
	# 	self.assertEqual(profile.tempo, 0.0)
	# 	self.assertEqual(profile.speechiness, 1.0)
	# 	self.assertEqual(profile.energy, 0.5)

	def test_user_exist(self):
		num_results = User.objects.filter(email="harry.potter@live.com").count()
		self.assertEqual(num_results,1)

	# def test_profile_exist(self):
	# 	user = User.objects.get(email="harry.potter@live.com")
	# 	profile = Profile.objects.filter(userid=user).count()
	# 	self.assertEqual(profile,1)

	def test_update_db(self):
		user = User.objects.get(email="harry.potter@live.com")
		user.first_name = "Robert"
		user.last_name = "Pear"
		user.save()
		user = User.objects.get(email="harry.potter@live.com")
		self.assertEqual(user.first_name,"Robert")
		self.assertEqual(user.last_name,"Pear")

class ArtistTest(TestCase):
	def setUp(self):
		self.artist = Artist.objects.create(artist_name='Will',artist_spotify_id='BFB:nf3bfjk3bjkFBj2bf',artist_uri='hj3bfj3838BDSHBM3fF')

	def tearDown(self):
		Artist.objects.all().delete()

	def test_artist_attributes(self):
		artist = Artist.objects.get(artist_uri='hj3bfj3838BDSHBM3fF')
		self.assertEqual(artist.artist_name, 'Will')
		self.assertEqual(artist.artist_spotify_id, 'BFB:nf3bfjk3bjkFBj2bf')

	def test_update_db(self):
		artist = Artist.objects.get(artist_uri='hj3bfj3838BDSHBM3fF')
		artist.artist_name = 'Smith'
		artist.save()
		artist = Artist.objects.get(artist_uri='hj3bfj3838BDSHBM3fF')
		self.assertEqual(artist.artist_name,"Smith")

class AlbumTest(TestCase):
	def setUp(self):
		self.artist = Artist.objects.create(artist_name='Will',artist_spotify_id='BFB:nf3bfjk3bjkFBj2bf',artist_uri='hj3bfj3838BDSHBM3fF')
		self.album = Album.objects.create(artist=self.artist, album_name="some name", album_spotify_id='randomid', album_uri='random_uri')

	def tearDown(self):
		Artist.objects.all().delete()
		Album.objects.all().delete()

	def test_album_attributes(self):
		album = Album.objects.get(album_uri='random_uri')
		self.assertEqual(album.album_name, 'some name')
		self.assertEqual(album.album_spotify_id, 'randomid')

	def test_update_db(self):
		album = Album.objects.get(album_uri='random_uri')
		album.album_name = 'rookie'
		album.save()
		album = Album.objects.get(album_uri='random_uri')
		self.assertEqual(album.album_name,"rookie")

class TrackTest(TestCase):
	def setUp(self):
		self.artist = Artist.objects.create(artist_name='Will',artist_spotify_id='BFB:nf3bfjk3bjkFBj2bf',artist_uri='hj3bfj3838BDSHBM3fF')
		self.album = Album.objects.create(artist=self.artist, album_name="some name", album_spotify_id='randomid', album_uri='random_uri')
		self.track = Track.objects.create(album=self.album, artist=self.artist, track_name='Track Name', track_id='NAKLN3', track_uri='AJBKFJ',
			track_image='url', danceability=0.23, energy=0.82, loudness=-1.22, speechiness=3.97, acousticness=1.5, instrumentalness=0.5,
			liveness=0.0, valence=1.1, tempo=2.3)

	def tearDown(self):
		Artist.objects.all().delete()
		Album.objects.all().delete()
		Track.objects.all().delete()

	def test_track_attributes(self):
		track = Track.objects.get(track_id='NAKLN3')
		self.assertEqual(track.album.album_name, 'some name')
		self.assertEqual(track.energy, 0.82)
		self.assertEqual(track.loudness, -1.22)
		self.assertEqual(track.speechiness, 3.97)
		self.assertEqual(track.valence, 1.1)
		self.assertEqual(track.tempo, 2.3)

	def test_update_db(self):
		track = Track.objects.get(track_id='NAKLN3')
		track.energy = 0.99
		track.loudness = 5.2
		track.speechiness = 1.2
		track.valence = 0.2
		track.tempo = 1.2
		track.save()
		track = Track.objects.get(track_id='NAKLN3')
		self.assertEqual(track.energy,0.99)
		self.assertEqual(track.loudness, 5.2)
		self.assertEqual(track.speechiness,1.2)
		self.assertEqual(track.valence, 0.2)
		self.assertEqual(track.tempo,1.2)
