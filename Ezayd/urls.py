from django.contrib import admin
from django.urls import path
from django.urls import include
from .views import *

urlpatterns = [
    path('accueil',accueil,name='accueil'),  
]
