# views.py
""" Put views here """

import os
#from django.http import Http404
#from django.http import HttpResponse
from django.shortcuts import render
#from django.conf import settings
#from django.contrib.auth.decorators import login_required
#from django.shortcuts import get_object_or_404
from django.contrib.sitemaps import Sitemap
#from django.core.paginator import Paginator
from django.urls import reverse
#from django.conf import settings
#from django.contrib.auth.models import User
from keys.models import Keys
#from stats.models import Stats

def index(request):
    """ main index view """
    return render(request, 'index.html')

class KeySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        keys = Keys.objects.all()
        #paginator = Paginator(keys, settings.KEYSETS_PAGINATE_BY)
        #return keys, paginator.page_range
        return keys

    def seen(self, obj):
        return obj.seen

    #def location(self, page):
    #    return reverse('key_index')

class Sitemap(Sitemap):
    changefreq = "hourly"
    priority = 0.5

    def items(self):
        #keys = Keys.objects.all()
        #paginator = Paginator(keys, settings.KEYSETS_PAGINATE_BY)
        #return ['index', 'stat_index', 'key_index'], paginator.page_range
        return ['index', 'stat_index', 'key_index']

    def location(self, item):
        return reverse(item)

class DatastoreSitemap(Sitemap):
    changefreq = "hourly"
    priority = 0.5

    def items(self):
        _subfolders = [f.path for f in os.scandir('datastore') if f.is_dir()]
        subfolders = []

        for _subfolder in _subfolders:
            if "demo" not in _subfolder:
                _s = "/" + _subfolder + "/"
                subfolders.append(_s)
        subfolders.append('/datastore/')
        return subfolders

    def location(self, item):
        return item
