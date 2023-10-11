from django.conf.urls import url
from . import views
import os
if os.path.exists('OTP.txt'):
	os.remove('OTP.txt')
urlpatterns = [
	url('', views.index, name='index'),
]
