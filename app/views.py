# views.py
""" Put views here """

from django.http import Http404
#from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

def index(request):
    """ main index view """
    return render(request, 'index.html')
