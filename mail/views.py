from django.shortcuts import render

# Create your views here.
from django.core.mail import send_mail
from django.http import HttpResponse
# Create your views here.
def sendSimpleEmail(request):
    subject = 'Enter the Subject of email'
    message = 'hii,write your text here.'
    email_from = 'shwethakp111@gmail.com'
    recipient = ['shwethasuvarna681@gmail.com']
    res = send_mail( subject, message, email_from, recipient)
    return HttpResponse('%s'%res)