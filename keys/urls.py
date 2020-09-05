from django.urls import path
#from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.key_index, name='key_index'),
    path('<str:shortkey>/', views.key_view, name='key_view'),
    #path('<str:shortkey>/dat/', views.key_dat_view, name='key_dat_view'),
]
