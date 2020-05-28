from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import path, include, reverse, resolve
from datetime import datetime as dt, date
from mainapp.models import Artist,Album,Track,Profile,Rating
from mainapp.views import *
# python manage.py test mainapp/tests

class URLSTest(TestCase):
	def test_sign_up(self):
		url = reverse('mainapp:sign_up')
		self.assertEqual(resolve(url).func, sign_up)
		self.assertEqual(resolve(url).url_name, "sign_up")

		response = self.client.get(reverse('mainapp:sign_up'))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'mainapp/sign_up.html')

	def test_login(self):
		url = reverse('mainapp:login')
		self.assertEqual(resolve(url).func, login)
		self.assertEqual(resolve(url).url_name, "login")

		response = self.client.get(reverse('mainapp:login'))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'mainapp/login.html')

	def test_password_request(self):
		url = reverse('mainapp:password_request')
		self.assertEqual(resolve(url).func, password_request)
		self.assertEqual(resolve(url).url_name, "password_request")

		response = self.client.get(reverse('mainapp:password_request'))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'mainapp/password_request.html')

	def test_profile(self):
		url = reverse('mainapp:profile')
		self.assertEqual(resolve(url).func, profile)
		self.assertEqual(resolve(url).url_name, "profile")

		response = self.client.get(reverse('mainapp:profile'))
		self.assertEqual(response.status_code, 302)
		# self.assertTemplateUsed(response, 'mainapp/profile.html')

	def test_index(self):
		url = reverse('mainapp:index')
		self.assertEqual(resolve(url).func, index)
		self.assertEqual(resolve(url).url_name, "index")

		response = self.client.get(reverse('mainapp:index'))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'mainapp/index.html')

	def test_library(self):
		url = reverse('mainapp:library')
		self.assertEqual(resolve(url).func, library)
		self.assertEqual(resolve(url).url_name, "library")

		response = self.client.get(reverse('mainapp:library'))
		self.assertEqual(response.status_code, 302)
		# self.assertTemplateUsed(response, 'mainapp/library.html')