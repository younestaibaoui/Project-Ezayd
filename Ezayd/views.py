from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Enchaire
from django.utils import timezone
from django.shortcuts import render
from django.utils import timezone
from .models import Enchaire
from django.shortcuts import render
from django.utils import timezone

import random

def accueil(request):
    enchaires = Enchaire.objects.select_related('lot').all()

    for enchere in enchaires:
        enchere.images = {
            'voitures': [],
            'immobiliers': [],
            'materiels': [],
            'informatique': [],
            'mobilier': [],
            'bijoux': [],
            'stocks': [],
        }

        lot = enchere.lot
        all_images = []

        # --- Remplir toutes les images par catégorie ---
        for voiture in lot.voitures.all():
            for img in voiture.images.all():
                url = img.image.url
                enchere.images['voitures'].append(url)
                all_images.append(url)

        for immo in lot.immobiliers.all():
            for img in immo.images.all():
                url = img.image.url
                enchere.images['immobiliers'].append(url)
                all_images.append(url)

        for materiel in lot.materiels.all():
            for img in materiel.images.all():
                url = img.image.url
                enchere.images['materiels'].append(url)
                all_images.append(url)

        for info in lot.informatique.all():
            for img in info.images.all():
                url = img.image.url
                enchere.images['informatique'].append(url)
                all_images.append(url)

        for mob in lot.mobilier.all():
            for img in mob.images.all():
                url = img.image.url
                enchere.images['mobilier'].append(url)
                all_images.append(url)

        for bijou in lot.bijoux.all():
            for img in bijou.images.all():
                url = img.image.url
                enchere.images['bijoux'].append(url)
                all_images.append(url)

        for stock in lot.stocks.all():
            if hasattr(stock, 'images'):
                for img in stock.images.all():
                    url = img.image.url
                    enchere.images['stocks'].append(url)
                    all_images.append(url)

        # --- Choisir une image aléatoire comme image principale ---
        enchere.main_image_url = random.choice(all_images) if all_images else None


    return render(request, 'accueil.html', {'enchaires': enchaires})



from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Enchaire

@require_POST
@login_required
def toggle_favori(request, enchere_id):
    enchere = get_object_or_404(Enchaire, id=enchere_id)
    if request.user in enchere.savers.all():
        enchere.savers.remove(request.user)
    else:
        enchere.savers.add(request.user)
    return redirect('accueil')  # Redirige vers la page principale




# -----------------------------------------------------------------

# views.py

from django.shortcuts import render

def search_view(request):
    query = request.GET.get('q', '')
    # Tu peux filtrer tes objets ici selon le modèle (exemple avec un modèle fictif)
    results = []  # Exemple : Enchere.objects.filter(titre__icontains=query)
    return render(request, 'search.html', {'query': query, 'results': results})


def panier_view(request):
    # Exemple : récupérer le panier de l'utilisateur
    panier_items = []  # Exemple : Panier.objects.filter(user=request.user)
    return render(request, 'panier.html', {'items': panier_items})

def profil_view(request):
    return render(request, 'profil.html')

