"""cuneiform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.contrib.sitemaps.views import sitemap
#from django.conf.urls import url
#from organizations.backends import invitation_backend
from . import views
from keys.views import KeySitemap

sitemaps = {'KeySitemap': KeySitemap}

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('keys/', include('keys.urls'), name='key_index'),
    path('stats/', include('stats.urls'), name='stat_index'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
]
