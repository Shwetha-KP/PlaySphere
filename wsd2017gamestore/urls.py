"""wsd2017gamestore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls import *
from django.contrib import admin
from django.conf import settings
from mail import views as mails
from verification import views


urlpatterns = [
	url(r'^admin/', admin.site.urls),
	url(r'^$', include('store.urls')),
	url(r'^signup/', include('registration.urls')),
	url(r'^auth/', include('authentication.urls')),
	url(r'^game/', include('gameview.urls')),
	url(r'^dev/', include('developer.urls')),
    url("^soc/", include("social_django.urls", namespace="social")),
    url('mail/',mails.sendSimpleEmail,name="mail"),
   
    #url('', views.register, name='register'),
   # path('otp/', views.otpVerify,name="login"),
    #url('otp/<str:uid>/', views.otpVerify, name='otp'),
    #url('home', views.home, name='home'),
]

