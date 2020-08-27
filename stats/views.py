# views.py
""" Put views here """

from django.http import Http404
#from django.views.generic.edit import CreateView, UpdateView, DeleteView
#from django.urls import reverse_lazy
#from django.http import HttpResponse
#from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
#from django.utils import timezone
#from .models import Keys, Stats

def stat_index(request):
    """ stat index """

    return render(request, 'stat_index.html')
