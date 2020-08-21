# views.py
""" Put views here """

#from django.http import Http404
#from django.views.generic.edit import CreateView, UpdateView, DeleteView
#from django.urls import reverse_lazy
#from django.http import HttpResponse
#from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
#from django.shortcuts import render, redirect
#from django.utils import timezone
from .models import Eks, Tek

def index(request):
    """ index """
    return render(request, 'index.html')

#def IndexView(request):
#    """ view """
#    context = {}
#    return render(request, 'index.html', context)
