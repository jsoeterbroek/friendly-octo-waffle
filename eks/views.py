# views.py
""" Put views here """

#from django.http import Http404
#from django.views.generic.edit import CreateView, UpdateView, DeleteView
#from django.urls import reverse_lazy
#from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
#from django.utils import timezone
from .models import Eks

def index(request):
    """ keysets view with pagination """

    keysets_list_latest = Eks.objects.order_by('-seen')
    paginator = Paginator(keysets_list_latest, 20)
    page = request.GET.get('page')
    try:
        plist = paginator.get_page(page)
    except PageNotAnInteger:
        plist = paginator.get_page(1)
    except EmptyPage:
        plist = paginator.get_page(paginator.num_pages)

    context = {'plist': plist}
    return render(request, 'index.html', context)

#def IndexView(request):
#    """ view """
#    context = {}
#    return render(request, 'index.html', context)
