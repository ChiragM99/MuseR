from django.urls import path, include
from mainapp import views

app_name = "mainapp"
urlpatterns = [
	path('', views.index, name='index'),
	path('sign_up/', views.sign_up, name='sign_up'),
	path('log_out/', views.log_out, name='log_out'),
	path('login/', views.login, name='login'),
	path('profile/', views.profile, name='profile'),
	path('library/', views.library, name='library'),
	path('track_page/<int:id>/', views.track_page, name='track_page'),
	path('activate/<uidb64>/<token>', views.activateaccount, name='activate'),
	path('password_request/', views.password_request, name='password_request'),
	path('password_change/<uidb64>/<token>', views.password_change, name='password_change'),
	path('search_page/', views.search_page, name='search_page'),
]