import random

from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import Http404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Count, Q

from perso.models import UserAccount

from .models import (
    Enchaire,
    EnchaireObjet,
    Lot,
    Voiture,
    Immobilier,
    MaterielProfessionnel,
    InformatiqueElectronique,
    MobilierEquipement,
    BijouxObjetValeur,
    StockInvendu,
    OeuvreCollection,
    DemandeEnchaire,
    ParticipationEnchaire
)

def accueil(request):
    # Get search parameter from request
    search_query = request.GET.get('search', '')
  
    # Base query with select_related
    enchaires = Enchaire.objects.select_related('lot').all()
  
    # Apply search filter if provided
    if search_query:
        enchaires = enchaires.filter(lot__nom__icontains=search_query)

    # Récupérer les top 3 objets par catégorie avec images aléatoires
    top_objets_by_category = get_top_3_objets_by_category()

    # Traitement des enchères existantes (votre code original)
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
        'search_query': search_query,
        'top_objets_by_category': top_objets_by_category,
    }

    # Vérifier si l'utilisateur est authentifié et récupérer les notifications
    if request.user.is_authenticated:
        notifications = request.user.notifications.all() if request.user.is_authenticated else None
        if notifications:
            unread_count = notifications.filter(is_read=False).count()
        else:
            unread_count = 0
    
        # Récupérer les notifications de l'utilisateur connecté
        notifications = request.user.notifications.all().order_by('-created_at')    
        context['unread_count'] = unread_count
        context['notifications'] = notifications

    return render(request, 'accueil/accueil.html', context)

def get_top_3_objets_by_category():
    """
    Récupère les top 3 objets par nombre de participations pour chaque catégorie
    avec une image aléatoire pour chaque objet
    """
    # Dictionnaire pour mapper les types aux modèles
    type_models = {
        'vehicules': Voiture,
        'immobilier': Immobilier,
        'materiel_pro': MaterielProfessionnel,
        'informatique_electronique': InformatiqueElectronique,
        'mobilier_equipements': MobilierEquipement,
        'bijoux_objets_valeur': BijouxObjetValeur,
        'stocks_invendus': StockInvendu,
        'oeuvres_collections': OeuvreCollection,
    }
    
    # Dictionnaire pour les icônes par catégorie
    category_icons = {
        'vehicules': 'fas fa-car',
        'immobilier': 'fas fa-home',
        'materiel_pro': 'fas fa-tools',
        'informatique_electronique': 'fas fa-laptop',
        'mobilier_equipements': 'fas fa-couch',
        'bijoux_objets_valeur': 'fas fa-gem',
        'stocks_invendus': 'fas fa-boxes',
        'oeuvres_collections': 'fas fa-palette',
    }
    
    # Dictionnaire pour les noms des catégories
    category_names = {
        'vehicules': 'Véhicules',
        'immobilier': 'Immobilier',
        'materiel_pro': 'Matériel professionnel',
        'informatique_electronique': 'Informatique & électronique',
        'mobilier_equipements': 'Mobilier & équipements',
        'bijoux_objets_valeur': 'Bijoux & objets de valeur',
        'stocks_invendus': 'Stocks et invendus',
        'oeuvres_collections': 'Œuvres & collections',
    }
    
    top_objets = []
    
    for type_key, model_class in type_models.items():
        try:
            # Récupérer les objets de cette catégorie avec le nombre de participations
            objets = model_class.objects.select_related(
                'enchaireObjet', 'lot', 'lot__enchaire'
            ).annotate(
                participation_count=Count('enchaireObjet__participations', distinct=True)
            ).filter(
                lot__enchaire__etat='active',  # Seulement les enchères actives
                participation_count__gt=0  # Seulement ceux avec des participations
            ).order_by('-participation_count')[:1]  # Top 1 par catégorie
            
            if objets.exists():
                top_objet = objets.first()
                
                # Calculer les jours restants
                today = timezone.now().date()
                jours_restants = (top_objet.lot.enchaire.date_fin - today).days

                # Récupérer les images
                images = []
                if hasattr(top_objet, 'images'):
                    images = [img.image.url for img in top_objet.images.all()[:3]]

                # Déterminer le titre selon la catégorie
                if type_key == 'vehicules' and hasattr(top_objet, 'voiture'):
                    title = f"{top_objet.voiture.nom} - {top_objet.voiture.model}"
                elif type_key == 'immobilier' and hasattr(top_objet, 'immobilier'):
                    title = top_objet.immobilier.titre
                elif type_key == 'materiel_pro' and hasattr(top_objet, 'materielProfessionnel'):
                    title = top_objet.materielProfessionnel.nom
                elif type_key == 'informatique_electronique' and hasattr(top_objet, 'informatiqueElectronique'):
                    title = f"{top_objet.InformatiqueElectronique.marque}"
                elif type_key == 'mobilier_equipements' and hasattr(top_objet, 'mobilierEquipement'):
                    title = top_objet.mobilierEquipement.categorie
                elif type_key == 'bijoux_objets_valeur' and hasattr(top_objet, 'bijouxObjetValeur'):
                    title = top_objet.bijouxObjetValeur.type_objet
                elif type_key == 'stocks_invendus' and hasattr(top_objet, 'stockInvendu'):
                    title = top_objet.stockInvendu.nom_produit
                elif type_key == 'oeuvres_collections' and hasattr(top_objet, 'oeuvreCollection'):
                    title = top_objet.oeuvreCollection.titre
                else:
                    title = str(top_objet)

                # Créer l'objet de données
                objet_data = {
                    'title': title,
                    'type': type_key,
                    'category_name': category_names.get(type_key, 'Autre'),
                    'category_icon': category_icons.get(type_key, 'fa-question'),
                    'participation_count': top_objet.participation_count,
                    'price_current': top_objet.enchaireObjet.price_reserved if top_objet.enchaireObjet else 0,
                    'jours_restants': max(0, jours_restants),
                    'images': images,
                    'main_image': random.choice(images) if images else '/static/images/placeholder.jpg',
                    'enchaire': top_objet.lot.enchaire,
                    'objet': top_objet,
                    'views': random.randint(10, 500),  # Simuler des vues
                    'favorites': random.randint(1, 50),  # Simuler des favoris
                }

                top_objets.append(objet_data)

        except Exception as e:
            # Log l'erreur mais continue avec les autres catégories
            print(f"Erreur pour la catégorie {type_key}: {e}")
            continue
    
    # Mélanger la liste pour avoir un ordre aléatoire dans le carrousel
    random.shuffle(top_objets)
    
    return top_objets

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

    participations = ParticipationEnchaire.objects.filter(
        enchaireObjet__in=[obj.enchaireObjet for obj in objets if obj.enchaireObjet]
    ).values('user').distinct()

    participation_count = participations.count()

    context = {
        'enchaire' : enchaire,
        'demande' : demande if request.user.is_authenticated else None,
        'lot' : lot,
        'objets' : objets,
        'participation_count': participation_count,

    }
    
    if request.user.is_authenticated:
        notifications = request.user.notifications.all() if request.user.is_authenticated else None
        if notifications:
            unread_count = notifications.filter(is_read=False).count()
        else:
            unread_count = 0
    
        # Récupérer les notifications de l'utilisateur connecté
        notifications = request.user.notifications.all().order_by('-created_at')    
        context['unread_count'] = unread_count
        context['notifications'] = notifications

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

    is_winner = False
    if request.user.is_authenticated:
        winner = enchaireObjet.winner

        if winner and winner == request.user:
            is_winner = True 

    demande = DemandeEnchaire.objects.filter(user=request.user, enchaire=enchaire).first() if request.user.is_authenticated else None
    demande_state = demande.state if demande else None
   
    participations = enchaireObjet.participations.all().order_by('-date_participation') if enchaireObjet else None
    participation_count = participations.values('user').distinct().count() if participations else 0

    context = {
        'enchaire_id': enchaire,
        'type_objet': type_objet,
        'objet': objet, 
        'enchaireObjet': enchaireObjet,
        'participations': participations, 
        'participation_count' : participation_count,
        'is_winner': is_winner,
        'demande_state': demande_state,  
    }
    
    if request.user.is_authenticated:
        notifications = request.user.notifications.all() if request.user.is_authenticated else None
        if notifications:
            unread_count = notifications.filter(is_read=False).count()
        else:
            unread_count = 0
    
        # Récupérer les notifications de l'utilisateur connecté
        notifications = request.user.notifications.all().order_by('-created_at')    
        context['unread_count'] = unread_count
        context['notifications'] = notifications

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

@login_required
def profil_view(request):

    if request.user.is_authenticated:
        context = {}
        context['user'] = request.user
    else:
        redirect('connexion')  
    
    if request.user.is_authenticated:
        notifications = request.user.notifications.all() if request.user.is_authenticated else None
        if notifications:
            unread_count = notifications.filter(is_read=False).count()
        else:
            unread_count = 0
    
        # Récupérer les notifications de l'utilisateur connecté
        notifications = request.user.notifications.all().order_by('-created_at')    
        context['unread_count'] = unread_count
        context['notifications'] = notifications

    return render(request, 'profil.html', context)

@require_POST
@login_required
def participer(request):

    user = request.user
    type_objet = request.POST.get('type_objet')
    objet_id = request.POST.get('objet_id')

    if not objet_id or not type_objet:
        raise Http404("Something is missing.")
    
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

    demande = user.demandes_enchaire.all().first() if request.user.is_authenticated else None
    demande_state = demande.state if demande else None
    enchaireObjet = objet.enchaireObjet

    if not enchaireObjet:
        raise Http404("EnchaireObjet not found.")
    
    if (enchaireObjet.winner and enchaireObjet.winner == user):
        raise Http404("You are already the runner up winner.")
    elif  demande_state != 'Approuvée':
        raise Http404("You must have an approved request to participate in this auction.")
    else:
        enchaireObjet.participer(user)

    return redirect('details_objet', type_objet, objet_id)

@login_required
def mes_participations(request):

    user = request.user
    participations = user.participations_encheres.values('enchaireObjet').distinct().order_by('-date_participation')

    for participation in participations:
        
        enchaireObjet = get_object_or_404(EnchaireObjet, id=participation['enchaireObjet'])
        type_objet = enchaireObjet.get_type()

        if type_objet == 'vehicules':
            objet = enchaireObjet.voiture
        elif type_objet == 'immobilier':
            objet = enchaireObjet.immobilier
        elif type_objet == 'materiel_pro':
            objet = enchaireObjet.materielProfessionnel
        elif type_objet == 'informatique_electronique':
            objet = enchaireObjet.informatiqueElectronique
        elif type_objet == 'mobilier_equipements':
            objet = enchaireObjet.mobilierEquipement
        elif type_objet == 'bijoux_objets_valeur':
            objet = enchaireObjet.bijouxObjetValeur
        elif type_objet == 'stocks_invendus':
            objet = enchaireObjet.stockInvendu
        elif type_objet == 'oeuvres_collections':
            objet = enchaireObjet.oeuvreCollection

        participation['objet'] = objet
        participation['enchere'] = objet.lot.enchaire

    context = {
        'participations': participations,
    }

    notifications = request.user.notifications.all() if request.user.is_authenticated else None
    if notifications:
        unread_count = notifications.filter(is_read=False).count()
    else:
        unread_count = 0

    # Récupérer les notifications de l'utilisateur connecté
    notifications = request.user.notifications.all().order_by('-created_at')    
    context['unread_count'] = unread_count
    context['notifications'] = notifications

    return render(request, 'mes_participations/mes_participations.html', context)