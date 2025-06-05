from django.contrib import admin
from django.urls import path
from django.urls import include
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from . import views

urlpatterns = [
    path('', accueil, name='accueil'),
    path("favori/<int:enchere_id>/", views.toggle_favori, name="toggle_favori"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
