from django.contrib import admin
from django.urls import path
from django.urls import include
from perso import views
from Ezayd.views import accueil

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Ezayd.urls')),
    # path('perso/', include('perso.urls')),  
    path('accueil/', accueil, name='accueil'),  # accessible via /accueil/
    path('inscription/', views.inscription_view, name='inscription'),
    path('', views.connexion_view, name='connexion'),
    path('deconnexion/', views.deconnexion_view, name='deconnexion'), 
    path('email-verification/<uuid:token>/', views.email_verification_view, name='email_verification'),
]
