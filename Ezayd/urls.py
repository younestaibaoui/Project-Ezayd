from django.contrib import admin
from django.urls import path
from django.urls import include
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

urlpatterns = [
    path('', accueil, name='accueil'),
    path("favori/<int:enchere_id>/", toggle_favori, name="toggle_favori"),
    path('details/<int:enchere_id>/', details_view, name='details_enchaire'),
    path('details-objet/<str:type_objet>/<int:objet_id>/', details_objet_view, name='details_objet'),
    # 🔍 Barre de recherche
    path('search/', search_view, name='search'),

    # 🛒 Panier
    path('panier/', panier_view, name='panier'),

    path('profil/', profil_view, name='profil'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
