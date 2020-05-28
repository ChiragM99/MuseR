from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from PIL import Image
from django.conf import settings

# Create your models here.

class Profile(models.Model):
	user = models.OneToOneField(User,on_delete=models.CASCADE)
	tempo = models.FloatField(default=0.0)
	speechiness = models.FloatField(default=0.0)
	energy = models.FloatField(default=0.0)
	profilepic = models.ImageField(default='default.png', upload_to='profile_pic')

	def __str__(self):
		return f'{self.user.username} Profile'

	def save(self, **kwargs):
		super().save()

		pic = Image.open(self.profilepic.path)

		if pic.height > 400 or pic.width > 400:
			output_size = (400, 400)
			pic.thumbnail(output_size)
			pic.save(self.profilepic.path)

class Artist(models.Model):
	artist_name = models.CharField(max_length=128)
	artist_spotify_id = models.CharField(max_length=128)
	artist_uri = models.CharField(max_length=128)

	def __str__ (self):
		return self.artist_name

class Album(models.Model):
	artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
	album_name = models.CharField(max_length=128)
	album_spotify_id = models.CharField(max_length=128)
	album_uri = models.CharField(max_length=128)

	def __str__ (self):
		return self.album_name

class Track(models.Model):
	album = models.ForeignKey(Album, on_delete=models.CASCADE)
	artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
	track_name = models.CharField(max_length=128)
	track_id = models.CharField(max_length=128)
	track_uri = models.CharField(max_length=128)
	track_image = models.CharField(max_length=1024)
	danceability = models.FloatField(default=0.0)
	energy = models.FloatField(default=0.0)
	loudness = models.FloatField(default=0.0)
	speechiness = models.FloatField(default=0.0)
	acousticness = models.FloatField(default=0.0)
	instrumentalness = models.FloatField(default=0.0)
	liveness = models.FloatField(default=0.0)
	valence = models.FloatField(default=0.0)
	tempo = models.FloatField(default=0.0)
	favourites = models.ManyToManyField(User, related_name='favourites', default="none")

	def __str__ (self):
		return self.track_name

class Rating(models.Model):
	track = models.ForeignKey(Track, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	rating_value = models.IntegerField(default=0)
	description = models.CharField(max_length=2048, default="")
	created_at = models.DateTimeField()