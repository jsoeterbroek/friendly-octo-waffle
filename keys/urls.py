from django.urls import path
#from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:shortkey>/', views.key_view, name='key-view'),
]
