from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import *

urlpatterns = [
    path('', accueil, name='accueil'),
    path("favori/<int:enchere_id>/", toggle_favori, name="toggle_favori"),
    path('details/<int:enchere_id>/', details_view, name='details_enchaire'),
    path('details-objet/<str:type_objet>/<int:objet_id>/', details_objet_view, name='details_objet'),
    path('demande/', demande, name='demande'),
    path('mes-participations/', mes_participations, name='mes_participations'),
    path('profil/', profil_view, name='profil'),
    path('participer/', participer, name='participer'),
    path('favoris/',favoris,name='favoris'),

    path('add_pfp/',add_pfp,name='add_pfp'),
    path('remove_pfp/',remove_pfp,name='remove_pfp'),
    # API Search
    path('api/search/', search_api, name='search_api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
