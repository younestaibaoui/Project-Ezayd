import random

from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from perso.models import UserAccount

from .models import (
    Enchaire,
    Voiture,
    Immobilier,
    MaterielProfessionnel,
    InformatiqueElectronique,
    MobilierEquipement,
    BijouxObjetValeur,
    StockInvendu,
    OeuvreCollection,
    DemandeEnchaire
)


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

  

    context = {
        'enchaires': enchaires,
    }

    notifications = request.user.notifications.all() if request.user.is_authenticated else None
    if notifications:
        unread_count = notifications.filter(is_read=False).count()
    else:
        unread_count = 0

    context['unread_count'] = unread_count


    return render(request, 'accueil/accueil.html', context)

@require_POST
@login_required
def toggle_favori(request, enchere_id):
    enchere = get_object_or_404(Enchaire, id=enchere_id)
    if request.user in enchere.savers.all():
        enchere.savers.remove(request.user)
    else:
        enchere.savers.add(request.user)
    return redirect(request.META.get('HTTP_REFERER', 'accueil'))





def details_view(request, enchere_id):
     
    enchaire = get_object_or_404(Enchaire, id=enchere_id)
    lot = enchaire.lot

    if request.user.is_authenticated:
        demande = DemandeEnchaire.objects.filter(user=request.user, enchaire=enchaire).first()

    lot_type = lot.type

    objets = {}

    if lot_type == 'vehicules':
        objets = lot.voitures.all()
    elif lot_type == 'immobilier':
        objets = lot.immobiliers.all()
    elif lot_type == 'materiel_pro':
        objets = lot.materiels.all()
    elif lot_type == 'informatique_electronique':
        objets = lot.informatique.all()
    elif lot_type == 'mobilier_equipements':
        objets = lot.mobilier.all()
    elif lot_type == 'bijoux_objets_valeur':
        objets = lot.bijoux.all()
    elif lot_type == 'stocks_invendus':
        objets = lot.stocks.all()
    elif lot_type == 'oeuvres_collections':
        objets = lot.oeuvres.all()

    context = {
        'enchaire' : enchaire,
        'demande' : demande if request.user.is_authenticated else None,
        'lot' : lot,
        'objets' : objets,
    }
    
    notifications = request.user.notifications.all() if request.user.is_authenticated else None
    if notifications:
        unread_count = notifications.filter(is_read=False).count()
    else:
        unread_count = 0

    context['unread_count'] = unread_count

    return render(request, 'details_enchaire/details_enchaire.html', context)

def details_objet_view(request, type_objet, objet_id):

    if type_objet == 'vehicules':
        objet = get_object_or_404(Voiture, id=objet_id)
    elif type_objet == 'immobilier':
        objet = get_object_or_404(Immobilier, id=objet_id)
    elif type_objet == 'materiel_pro':
        objet = get_object_or_404(MaterielProfessionnel, id=objet_id)
    elif type_objet == 'informatique_electronique':
        objet = get_object_or_404(InformatiqueElectronique, id=objet_id)
    elif type_objet == 'mobilier_equipements':
        objet = get_object_or_404(MobilierEquipement, id=objet_id)
    elif type_objet == 'bijoux_objets_valeur':
        objet = get_object_or_404(BijouxObjetValeur, id=objet_id)
    elif type_objet == 'stocks_invendus':
        objet = get_object_or_404(StockInvendu, id=objet_id)
    elif type_objet == 'oeuvres_collections':
        objet = get_object_or_404(OeuvreCollection, id=objet_id)

    enchaire = objet.lot.enchaire.id
    enchaireObjet = objet.enchaireObjet

    context = {
        'enchaireObjet': enchaireObjet,
        'type_objet': type_objet,
        'objet': objet,
        'enchaire_id': enchaire,       
    }
    
    notifications = request.user.notifications.all() if request.user.is_authenticated else None
    if notifications:
        unread_count = notifications.filter(is_read=False).count()
    else:
        unread_count = 0

    context['unread_count'] = unread_count

    return render(request, 'details_objet/details_objet.html', context)

@require_POST
@login_required
def demande(request):
    user_id = request.POST.get('user')
    enchaire_id = request.POST.get('enchaire')

    if not user_id or not enchaire_id:
        raise Http404("User ID or Enchaire ID is missing.")

    user = get_object_or_404(UserAccount, id=user_id)
    enchaire = get_object_or_404(Enchaire, id=enchaire_id)

    if DemandeEnchaire.objects.filter(user=user, enchaire=enchaire).exists():
        raise Http404("Demande existante.")  # Properly raise, not return

    # Create and save the new Demande
    demande = DemandeEnchaire(user=user, enchaire=enchaire)
    demande.save()

    # Redirect to the referring page or fallback to a named route (e.g., 'accueil')
    return redirect(request.META.get('HTTP_REFERER', 'accueil'))

# -----------------------------------------------------------------

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

    if request.user.is_authenticated:
        context = {}
        context['user'] = request.user
    else:
        redirect('connexion')  
    
    notifications = request.user.notifications.all() if request.user.is_authenticated else None
    if notifications:
        unread_count = notifications.filter(is_read=False).count()
    else:
        unread_count = 0

    context['unread_count'] = unread_count

    return render(request, 'profil.html', context)
