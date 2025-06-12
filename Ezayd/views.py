import random

from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.http import Http404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from Ezayd.utils import lancer_mise_a_jour_enchere_thread



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

import random
from django.utils import timezone
from django.shortcuts import render
from .models import Enchaire, ParticipationEnchaire  # adapte les imports selon ton projet

def accueil(request):
    # Lancer la mise à jour des enchères en arrière-plan
    lancer_mise_a_jour_enchere_thread() 
    # Récupérer le paramètre de recherche dans la requête GET
    search_query = request.GET.get('search', '')

    # Récupérer toutes les enchères avec lot lié pour optimisation
    enchaires = Enchaire.objects.select_related('lot').all()

    # Appliquer un filtre si une recherche est fournie
    if search_query:
        enchaires = enchaires.filter(lot__nom__icontains=search_query)

    for enchere in enchaires:
        enchere.images = {
            'voitures': [],
            'immobiliers': [],
            'materiels': [],
            'informatique': [],
            'mobilier': [],
            'bijoux': [],
            'stocks': [],
            'oeuvres': [],
        }

        participations_count_ = {
            'vehicules': 0,
            'immobilier': 0,
            'materiel_pro': 0,
            'informatique_electronique': 0,
            'mobilier_equipements': 0,
            'bijoux_objets_valeur': 0,
            'stocks_invendus': 0,
            'oeuvres_collections': 0,
        }

        lot = enchere.lot
        all_images = []

        # Remplir images par catégorie
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

        for oeuvre in lot.oeuvres.all():
            for img in oeuvre.images.all():
                url = img.image.url
                enchere.images['oeuvres'].append(url)
                all_images.append(url)

        # Image principale aléatoire
        enchere.main_image_url = random.choice(all_images) if all_images else None

        # Récupérer tous les objets liés au lot pour récupérer les participations
        objets = []
        objets += list(lot.voitures.all())
        objets += list(lot.immobiliers.all())
        objets += list(lot.materiels.all())
        objets += list(lot.informatique.all())
        objets += list(lot.mobilier.all())
        objets += list(lot.bijoux.all())
        objets += list(lot.stocks.all())
        objets += list(lot.oeuvres.all())

        # Extraire les objets ayant un attribut enchaireObjet (sûr que tous les objets en ont ?)
        objets_avec_enchaire = [obj.enchaireObjet for obj in objets if hasattr(obj, 'enchaireObjet') and obj.enchaireObjet]

        # Récupérer les participations distinctes par user sur ces objets
        participations = ParticipationEnchaire.objects.filter(enchaireObjet__in=objets_avec_enchaire).values_list('user', flat=True).distinct()

        # Stocker le nombre de participants dans un attribut dynamique
        enchere.participant_count = participations.count()
    
    # Define these somewhere globally or pass as parameters
    category_names = {
        'vehicules': 'Véhicules',
        'immobilier': 'Immobilier',
        'materiel_pro': 'Matériel Pro',
        'informatique_electronique': 'Informatique & Électronique',
        'mobilier_equipements': 'Mobilier & Équipements',
        'bijoux_objets_valeur': 'Bijoux & Objets de valeur',
        'stocks_invendus': 'Stocks & Invendus',
        'oeuvres_collections': 'Œuvres & Collections',
    }

    category_icons = {
        'vehicules': 'fa-car',
        'immobilier': 'fa-building',
        'materiel_pro': 'fa-cogs',
        'informatique_electronique': 'fa-laptop',
        'mobilier_equipements': 'fa-couch',
        'bijoux_objets_valeur': 'fa-gem',
        'stocks_invendus': 'fa-boxes',
        'oeuvres_collections': 'fa-palette',
    }

    top_objets_by_category = get_top_objets_by_category(enchaires, category_names, category_icons)

    context = {
        'enchaires': enchaires,
        'search_query': search_query,
        'top_objets_by_category': top_objets_by_category,
    }

    # Gestion des notifications pour utilisateur connecté
    if request.user.is_authenticated:
        notifications = request.user.notifications.all()
        unread_count = notifications.filter(is_read=False).count() if notifications else 0
        notifications = notifications.order_by('-created_at') if notifications else []

        context['unread_count'] = unread_count
        context['notifications'] = notifications

    return render(request, 'accueil/accueil.html', context)

from collections import defaultdict
from datetime import timedelta

def get_top_objets_by_category(enchaires, category_names, category_icons):
    top_by_category = {}
    categories_map = {
        'vehicules': 'voitures',
        'immobilier': 'immobiliers',
        'materiel_pro': 'materiels',
        'informatique_electronique': 'informatique',
        'mobilier_equipements': 'mobilier',
        'bijoux_objets_valeur': 'bijoux',
        'stocks_invendus': 'stocks',
        'oeuvres_collections': 'oeuvres',
    }

    for enchere in enchaires:
        if enchere.etat == 'active':
            lot = enchere.lot
            for category_key, lot_attr in categories_map.items():
                objets = getattr(lot, lot_attr).all()
                for objet in objets:
                    # Skip if no participation count can be computed
                    if not hasattr(enchere, 'participant_count'):
                        continue

                    # Keep top object by participation count
                    count = top_by_category.get('category_key').enchaireObjet.participations.values('user').distinct.count() if top_by_category.get('category_key') else 0
                    if category_key not in top_by_category or (enchere.participant_count > count and enchere.participant_count != 0):
                        objet.enchaireObjet = getattr(objet, 'enchaireObjet', None)
                        objet.lot = lot
                        objet.participation_count = enchere.participant_count
                        objet.enchere = enchere
                        top_by_category[category_key] = objet

    # Format the data
    top_objets_data = []
    for type_key, top_objet in top_by_category.items():
        # Time remaining logic
        now = timezone.now()
        end_time = top_objet.enchere.date_fin if top_objet.enchere and top_objet.enchere.date_fin else now
        # remaining = max(end_time - now, timedelta())
        # jours_restants = remaining.days
        # heures_restantes = remaining.seconds // 3600
        # minutes_restantes = (remaining.seconds % 3600) // 60
        # secondes_restantes = remaining.seconds % 60

        # Images
        images = []
        if hasattr(top_objet, 'images'):
            images = [img.image.url for img in top_objet.images.all()]

        objet_data = {
            'title': str(top_objet),
            'type': type_key,
            'category_name': category_names.get(type_key, 'Autre'),
            'category_icon': category_icons.get(type_key, 'fa-question'),
            'participation_count': top_objet.participation_count,
            'price_current': top_objet.enchaireObjet.price_reserved if top_objet.enchaireObjet else 0,
            # 'jours_restants': max(0, jours_restants),
            # 'heures_restantes': heures_restantes,
            # 'minutes_restantes': minutes_restantes,
            # 'secondes_restantes': secondes_restantes,
            'images': images,
            'main_image': random.choice(images) if images else '/static/images/placeholder.jpg',
            'enchaire': top_objet.enchere,
            'objet': top_objet,
        }

        if objet_data.get('participation_count') != 0:
            top_objets_data.append(objet_data)

    return top_objets_data

@require_POST
@login_required
def toggle_favori(request, enchere_id):
    enchere = get_object_or_404(Enchaire, id=enchere_id)
    if request.user in enchere.savers.all():
        enchere.savers.remove(request.user)
    else:
        enchere.savers.add(request.user)
    return redirect(request.META.get('HTTP_REFERER', 'accueil'))

from django.shortcuts import render, get_object_or_404
from .models import Enchaire, DemandeEnchaire, ParticipationEnchaire

def details_view(request, enchere_id):
    enchaire = get_object_or_404(Enchaire, id=enchere_id)
    lot = enchaire.lot
    lot_type = lot.type

    # Récupération de la demande de l'utilisateur
    demande = None
    if request.user.is_authenticated:
        demande = DemandeEnchaire.objects.filter(user=request.user, enchaire=enchaire).first()

    objets_queryset = []
    objets_info = []

    # Si le lot est de type "vehicules"
    if lot_type == 'vehicules':
        objets_queryset = lot.voitures.select_related('enchaireObjet').prefetch_related('enchaireObjet__participations').all()

        for voiture in objets_queryset:
            enchaire_objet = voiture.enchaireObjet
            participation_count = (
                enchaire_objet.participations.values('user').distinct().count()
                if enchaire_objet else 0
            )

            objets_info.append({
                'id': voiture.id,
                'nom': voiture.nom,
                'enchaireObjet': enchaire_objet,
                'get_images': voiture.get_images(),  # Suppose que ça retourne des URLs ou une liste
                'participation_count': participation_count,
                'model': voiture.model,
                'year': voiture.year,
            })

    # Si le lot est de type "immobilier"
    elif lot_type == 'immobilier':
        objets_queryset = lot.immobiliers.select_related('enchaireObjet').prefetch_related('enchaireObjet__participations').all()

        for immobilier in objets_queryset:
            enchaire_objet = immobilier.enchaireObjet
            participation_count = (
                enchaire_objet.participations.values('user').distinct().count()
                if enchaire_objet else 0
            )
            objets_info.append({
                'id': immobilier.id,
                'titre': immobilier.titre,
                'get_images': immobilier.get_images(),  # Suppose que ça retourne des URLs ou une liste
                'ville': immobilier.ville,
                'adresse': immobilier.adresse,
                'participation_count': participation_count,
                'surface': immobilier.surface,  # Si applicable
                'pieces': immobilier.nombre_pieces,  # Si applicable
            })

    # Si le lot est de type "materiel_pro"
    elif lot_type == 'materiel_pro':
        objets_queryset = lot.materiels.select_related('enchaireObjet').prefetch_related('enchaireObjet__participations').all()
        

        for materiel in objets_queryset:
            
            enchaire_objet = materiel.enchaireObjet
            participation_count = (
                enchaire_objet.participations.values('user').distinct().count()
                if enchaire_objet else 0
            )

            objets_info.append({
                'id': materiel.id,
                'nom': materiel.nom,
                'get_images': materiel.get_images(),  # Suppose que ça retourne des URLs ou une liste
                'marque': materiel.marque,
                'modele': materiel.modele,
                'participation_count': participation_count,
            })

    # Si le lot est de type "informatique_electronique"
    elif lot_type == 'informatique_electronique':
        objets_queryset = lot.informatique.select_related('enchaireObjet').prefetch_related('enchaireObjet__participations').all()


        for info in objets_queryset:
            enchaire_objet = info.enchaireObjet
            participation_count = (
                enchaire_objet.participations.values('user').distinct().count()
                if enchaire_objet else 0
            )


            objets_info.append({
                'id': info.id,
                'marque': info.marque,
                'modele': info.modele,
                'type_objet': info.type_objet,
                'get_images': info.get_images(),  # Suppose que ça retourne des URLs ou une liste
                'etat': info.etat,  # Si applicable
                'participation_count': participation_count,
                
            })

    # Si le lot est de type "mobilier_equipements"
    elif lot_type == 'mobilier_equipements':
        objets_queryset = lot.mobilier.all()
        for mobilier in objets_queryset:

            enchaire_objet = mobilier.enchaireObjet
            participation_count = (
                enchaire_objet.participations.values('user').distinct().count()
                if enchaire_objet else 0
            )

            objets_info.append({
                'id': mobilier.id,
                'categorie': mobilier.categorie,
                'get_images': mobilier.get_images(),  # Suppose que ça retourne des URLs ou une liste
                'participation_count': participation_count,
            })
    
    # Si le lot est de type "bijoux_objets_valeur"
    elif lot_type == 'bijoux_objets_valeur':
        objets_queryset = lot.bijoux.select_related('enchaireObjet').prefetch_related('enchaireObjet__participations').all()

        for bijou in objets_queryset:
            enchaire_objet = bijou.enchaireObjet
            participation_count = (
                enchaire_objet.participations.values('user').distinct().count()
                if enchaire_objet else 0
            )
            objets_info.append({
                'id': bijou.id,
                'type_objet': bijou.type_objet,
                'get_images': bijou.get_images(),  # Suppose que ça retourne des URLs ou une liste
                'caracteristiques': bijou.caracteristiques,  # Si applicable
                'participation_count': participation_count,
            })

    elif lot_type == 'stocks_invendus':
        objets_queryset = lot.stocks.select_related('enchaireObjet').prefetch_related('enchaireObjet__participations').all()

        for stock in objets_queryset:
            enchaire_objet = stock.enchaireObjet
            participation_count = (
                enchaire_objet.participations.values('user').distinct().count()
                if enchaire_objet else 0
            )
            objets_info.append({
                'id': stock.id,
                'nom_produit': stock.nom_produit,
                'get_images': stock.get_images(),  # Suppose que ça retourne des URLs ou une liste
                'quantite': stock.quantite,  # Si applicable
                'participation_count': participation_count,
            })
    # Si le lot est de type "oeuvres_collections"
    elif lot_type == 'oeuvres_collections':
        objets_queryset = lot.oeuvres.select_related('enchaireObjet').prefetch_related('enchaireObjet__participations').all()
        for oeuvre in objets_queryset:
            enchaire_objet = oeuvre.enchaireObjet
            participation_count = (
                enchaire_objet.participations.values('user').distinct().count()
                if enchaire_objet else 0
            )
            objets_info.append({
                'id': oeuvre.id,
                'titre': oeuvre.titre,
                'get_images': oeuvre.get_images(),  # Suppose que ça retourne des URLs ou une liste
                'artiste': oeuvre.artiste,
                'annee_creation': oeuvre.annee_creation,  # Si applicable
                'participation_count': participation_count,
            })
    else:
        raise Http404("Type de lot non supporté.")

    # Comptage des participations uniques
    participations = ParticipationEnchaire.objects.filter(
        enchaireObjet__in=[
            obj.enchaireObjet for obj in objets_queryset if obj.enchaireObjet
        ]
    ).values('user').distinct()
    participation_count = participations.count()

    # Notifications
    unread_count = 0
    notifications = []
    if request.user.is_authenticated:
        notifications = request.user.notifications.all().order_by('-created_at')
        unread_count = notifications.filter(is_read=False).count()

    context = {
        'enchaire': enchaire,
        'demande': demande,
        'lot': lot,
        'objets': objets_info,
        'participation_count': participation_count,
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'details_enchaire/details_enchaire.html', context)
  

# --------------------------------------------------------------------

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

    enchaire = objet.lot.enchaire
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
        'enchaire': enchaire,
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


    user = request.user
    
    if request.user.is_authenticated:
        notifications = request.user.notifications.all() if request.user.is_authenticated else None
        if notifications:
            unread_count = notifications.filter(is_read=False).count()
        else:
            unread_count = 0

    participations = ParticipationEnchaire.objects.filter(user=user)
    statistique_participation = {
        'total' : participations.values('enchaireObjet').distinct().count(),
        'remporte': participations.filter(enchaireObjet__reserved=True, enchaireObjet__winner=user).count(),
        'en_tete': participations.filter(enchaireObjet__reserved=False, enchaireObjet__winner=user).count(),
    }

    context = {
        'user': user,
        'unread_count': unread_count,
        'statistique_participation': statistique_participation,
    }


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

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

@login_required
def mes_participations(request):
    user = request.user
    # Récupérer toutes les participations triées par date décroissante
    participations_qs = user.participations_encheres.select_related('enchaireObjet').order_by('-date_participation')

    # Garder uniquement une participation par enchaireObjet (la plus récente)
    participations_distinctes = {}
    for participation in participations_qs:
        enchaire_obj_id = participation.enchaireObjet_id
        if enchaire_obj_id not in participations_distinctes:
            participations_distinctes[enchaire_obj_id] = participation

    participations = participations_distinctes.values()

    participations_detaillees = []

    for participation in participations:
        enchaireObjet = participation.enchaireObjet
        type_objet = enchaireObjet.type

        # Choix de l'objet selon le type
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
        else:
            objet = None

        if objet:
        
            participation_info = {
                'participation': participation,
                'objet': objet,
                'enchere': objet.lot.enchaire,
                'montant': participation.montant,
                'first_price': participation.enchaireObjet.price_reserved,
                'enchereObjet': enchaireObjet,
                'date_participation': participation.date_participation
            }

            participations_detaillees.append(participation_info)

    # Notifications
    notifications = user.notifications.all().order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()

    context = {
        'participations': participations_detaillees,
        'notifications': notifications,
        'unread_count': unread_count,
    }

    return render(request, 'mes_participations/mes_participations.html', context)

# ---------------------- search API ----------------------
from django.http import JsonResponse
from django.db.models import Q
from .models import (
    Voiture, Immobilier, MaterielProfessionnel, 
    InformatiqueElectronique, MobilierEquipement, 
    BijouxObjetValeur, StockInvendu, OeuvreCollection
)

def search_api(request):
    query = request.GET.get('q', '')
    results = []
    
    print(f"Recherche pour: '{query}'")  # Pour debug
    
    if query and len(query) >= 2:
        # Voitures
        try:
            voitures = Voiture.objects.all()[:5]
            print(f"Voitures trouvées: {voitures.count()}")
            
            for voiture in voitures:
                if query.lower() in voiture.nom.lower() or (voiture.model and query.lower() in voiture.model.lower()) or (voiture.marque and query.lower() in voiture.marque.lower()):
                    # Nom de la voiture
                    name = f"{voiture.nom} {voiture.model}" if voiture.model else voiture.nom
                    
                    # Image
                    image_url = None
                    try:
                        if hasattr(voiture, 'images') and voiture.images.exists():
                            image_url = voiture.images.first().image.url
                    except:
                        pass
                    
                    price = 150000  # Prix par défaut
                    try:
                        if hasattr(voiture, 'enchaireObjet') and voiture.enchaireObjet:
                            if voiture.enchaireObjet.price_reserved:
                                price = voiture.enchaireObjet.price_reserved
                    except:
                        pass
                    
                    # Nom d'enchère
                    auction_name = "Enchère non spécifiée"
                    try:
                        if hasattr(voiture, 'lot') and voiture.lot and hasattr(voiture.lot, 'enchaire') and voiture.lot.enchaire:
                            auction_name = voiture.lot.nom if hasattr(voiture.lot, 'nom') else f"Enchère #{voiture.lot.enchaire.id}"
                    except:
                        pass
                    
                    results.append({
                        'id': voiture.id,
                        'name': name,
                        'type': 'vehicules',
                        'category_name': 'Véhicules',
                        'auction_name': auction_name,
                        'price': price,
                        'image_url': image_url,
                        'ending_soon': False
                    })
                    print(f"Voiture ajoutée: {name}")
        except Exception as e:
            print(f"Erreur voitures: {e}")
        
        # Immobilier
        try:
            immobiliers = Immobilier.objects.all()[:5]
            print(f"Immobiliers trouvés: {immobiliers.count()}")
            
            for immobilier in immobiliers:
                if query.lower() in immobilier.titre.lower() or (immobilier.ville and query.lower() in immobilier.ville.lower()) or (immobilier.adresse and query.lower() in immobilier.adresse.lower()):
                    # Image
                    image_url = None
                    try:
                        if hasattr(immobilier, 'images') and immobilier.images.exists():
                            image_url = immobilier.images.first().image.url
                    except:
                        pass
                    
                    price = 250000  # Prix par défaut
                    try:
                        if hasattr(immobilier, 'enchaireObjet') and immobilier.enchaireObjet:
                            if immobilier.enchaireObjet.price_reserved:
                                price = immobilier.enchaireObjet.price_reserved
                    except:
                        pass
                    
                    # Nom d'enchère
                    auction_name = "Enchère non spécifiée"
                    try:
                        if hasattr(immobilier, 'lot') and immobilier.lot and hasattr(immobilier.lot, 'enchaire') and immobilier.lot.enchaire:
                            auction_name = immobilier.lot.nom if hasattr(immobilier.lot, 'nom') else f"Enchère #{immobilier.lot.enchaire.id}"
                    except:
                        pass
                    
                    results.append({
                        'id': immobilier.id,
                        'name': immobilier.titre,
                        'type': 'immobilier',
                        'category_name': 'Immobilier',
                        'auction_name': auction_name,
                        'price': price,
                        'image_url': image_url,
                        'ending_soon': False
                    })
                    print(f"Immobilier ajouté: {immobilier.titre}")
        except Exception as e:
            print(f"Erreur immobiliers: {e}")
        
        # Matériel Professionnel
        try:
            materiels = MaterielProfessionnel.objects.all()[:5]
            print(f"Matériels trouvés: {materiels.count()}")
            
            for materiel in materiels:
                if query.lower() in materiel.nom.lower() or (materiel.marque and query.lower() in materiel.marque.lower()) or (materiel.modele and query.lower() in materiel.modele.lower()): 
                    # Image
                    image_url = None
                    try:
                        if hasattr(materiel, 'images') and materiel.images.exists():
                            image_url = materiel.images.first().image.url
                    except:
                        pass
                    
                    price = 80000  # Prix par défaut
                    try:
                        if hasattr(materiel, 'enchaireObjet') and materiel.enchaireObjet:
                            if materiel.enchaireObjet.price_reserved:
                                price = materiel.enchaireObjet.price_reserved
                    except:
                        pass
                    
                    # Nom
                    name = materiel.nom
                    try:
                        if hasattr(materiel, 'marque') and materiel.marque:
                            name = f"{materiel.marque} {name}"
                    except:
                        pass
                    
                    # Nom d'enchère
                    auction_name = "Enchère non spécifiée"
                    try:
                        if hasattr(materiel, 'lot') and materiel.lot and hasattr(materiel.lot, 'enchaire') and materiel.lot.enchaire:
                            auction_name = materiel.lot.nom if hasattr(materiel.lot, 'nom') else f"Enchère #{materiel.lot.enchaire.id}"
                    except:
                        pass
                    
                    results.append({
                        'id': materiel.id,
                        'name': name,
                        'type': 'materiel_pro',
                        'category_name': 'Matériel Professionnel',
                        'auction_name': auction_name,
                        'price': price,
                        'image_url': image_url,
                        'ending_soon': False
                    })
                    print(f"Matériel ajouté: {name}")
        except Exception as e:
            print(f"Erreur matériels: {e}")

        # Informatique & Électronique
        try:
            informatiques = InformatiqueElectronique.objects.all()[:5]
            print(f"Informatiques trouvés: {informatiques.count()}")
            
            for info in informatiques:
                if (info.marque and query.lower() in info.marque.lower()) or (info.modele and query.lower() in info.modele.lower()) or (info.type_objet and query.lower() in info.type_objet.lower()):
                    # Image
                    image_url = None
                    try:
                        if hasattr(info, 'images') and info.images.exists():
                            image_url = info.images.first().image.url
                    except:
                        pass
                    
                    price = 50000  # Prix par défaut
                    try:
                        if hasattr(info, 'enchaireObjet') and info.enchaireObjet:
                            if info.enchaireObjet.price_reserved:
                                price = info.enchaireObjet.price_reserved
                    except:
                        pass
                    
                    # Nom
                    name_parts = []
                    if info.marque:
                        name_parts.append(info.marque)
                    if info.modele:
                        name_parts.append(info.modele)
                    name = " ".join(name_parts) if name_parts else f"Informatique #{info.id}"
                    
                    # Nom d'enchère
                    auction_name = "Enchère non spécifiée"
                    try:
                        if hasattr(info, 'lot') and info.lot and hasattr(info.lot, 'enchaire') and info.lot.enchaire:
                            auction_name = info.lot.nom if hasattr(info.lot, 'nom') else f"Enchère #{info.lot.enchaire.id}"
                    except:
                        pass
                    
                    results.append({
                        'id': info.id,
                        'name': name,
                        'type': 'informatique_electronique',
                        'category_name': 'Informatique & Électronique',
                        'auction_name': auction_name,
                        'price': price,
                        'image_url': image_url,
                        'ending_soon': False
                    })
                    print(f"Informatique ajouté: {name}")
        except Exception as e:
            print(f"Erreur informatiques: {e}")

        # Mobilier & Équipements
        try:
            mobiliers = MobilierEquipement.objects.all()[:5]
            print(f"Mobiliers trouvés: {mobiliers.count()}")
            
            for mobilier in mobiliers:
                if query.lower() in mobilier.categorie.lower() or (mobilier.materiau and query.lower() in mobilier.materiau.lower()) or (mobilier.couleur and query.lower() in mobilier.couleur.lower()):
                    # Image
                    image_url = None
                    try:
                        if hasattr(mobilier, 'images') and mobilier.images.exists():
                            image_url = mobilier.images.first().image.url
                    except:
                        pass
                    
                    price = 30000  # Prix par défaut
                    try:
                        if hasattr(mobilier, 'enchaireObjet') and mobilier.enchaireObjet:
                            if mobilier.enchaireObjet.price_reserved:
                                price = mobilier.enchaireObjet.price_reserved
                    except:
                        pass
                    
                    # Nom d'enchère
                    auction_name = "Enchère non spécifiée"
                    try:
                        if hasattr(mobilier, 'lot') and mobilier.lot and hasattr(mobilier.lot, 'enchaire') and mobilier.lot.enchaire:
                            auction_name = mobilier.lot.nom if hasattr(mobilier.lot, 'nom') else f"Enchère #{mobilier.lot.enchaire.id}"
                    except:
                        pass
                    
                    results.append({
                        'id': mobilier.id,
                        'name': mobilier.categorie,
                        'type': 'mobilier_equipements',
                        'category_name': 'Mobilier & Équipements',
                        'auction_name': auction_name,
                        'price': price,
                        'image_url': image_url,
                        'ending_soon': False
                    })
                    print(f"Mobilier ajouté: {mobilier.categorie}")
        except Exception as e:
            print(f"Erreur mobiliers: {e}")

        # Bijoux & Objets de Valeur
        try:
            bijoux = BijouxObjetValeur.objects.all()[:5]
            print(f"Bijoux trouvés: {bijoux.count()}")
            
            for bijou in bijoux:
                if query.lower() in bijou.type_objet.lower() or (bijou.matiere and query.lower() in bijou.matiere.lower()):
                    # Image
                    image_url = None
                    try:
                        if hasattr(bijou, 'images') and bijou.images.exists():
                            image_url = bijou.images.first().image.url
                    except:
                        pass
                    
                    price = 100000  # Prix par défaut
                    try:
                        if hasattr(bijou, 'enchaireObjet') and bijou.enchaireObjet:
                            if bijou.enchaireObjet.price_reserved:
                                price = bijou.enchaireObjet.price_reserved
                    except:
                        pass
                    
                    # Nom d'enchère
                    auction_name = "Enchère non spécifiée"
                    try:
                        if hasattr(bijou, 'lot') and bijou.lot and hasattr(bijou.lot, 'enchaire') and bijou.lot.enchaire:
                            auction_name = bijou.lot.nom if hasattr(bijou.lot, 'nom') else f"Enchère #{bijou.lot.enchaire.id}"
                    except:
                        pass
                    
                    results.append({
                        'id': bijou.id,
                        'name': bijou.type_objet,
                        'type': 'bijoux_objets_valeur',
                        'category_name': 'Bijoux & Objets de Valeur',
                        'auction_name': auction_name,
                        'price': price,
                        'image_url': image_url,
                        'ending_soon': False
                    })
                    print(f"Bijou ajouté: {bijou.type_objet}")
        except Exception as e:
            print(f"Erreur bijoux: {e}")

        # Stocks & Invendus
        try:
            stocks = StockInvendu.objects.all()[:5]
            print(f"Stocks trouvés: {stocks.count()}")
            
            for stock in stocks:
                if query.lower() in stock.nom_produit.lower():
                    # Image
                    image_url = None
                    try:
                        if hasattr(stock, 'images') and stock.images.exists():
                            image_url = stock.images.first().image.url
                    except:
                        pass
                    
                    price = 20000  # Prix par défaut
                    try:
                        if hasattr(stock, 'enchaireObjet') and stock.enchaireObjet:
                            if stock.enchaireObjet.price_reserved:
                                price = stock.enchaireObjet.price_reserved
                    except:
                        pass
                    
                    name = f"{stock.nom_produit} (x{stock.quantite})"
                    
                    # Nom d'enchère
                    auction_name = "Enchère non spécifiée"
                    try:
                        if hasattr(stock, 'lot') and stock.lot and hasattr(stock.lot, 'enchaire') and stock.lot.enchaire:
                            auction_name = stock.lot.nom if hasattr(stock.lot, 'nom') else f"Enchère #{stock.lot.enchaire.id}"
                    except:
                        pass
                    
                    results.append({
                        'id': stock.id,
                        'name': name,
                        'type': 'stocks_invendus',
                        'category_name': 'Stocks & Invendus',
                        'auction_name': auction_name,
                        'price': price,
                        'image_url': image_url,
                        'ending_soon': False
                    })
                    print(f"Stock ajouté: {name}")
        except Exception as e:
            print(f"Erreur stocks: {e}")

        # Œuvres & Collections
        try:
            oeuvres = OeuvreCollection.objects.all()[:5]
            print(f"Œuvres trouvées: {oeuvres.count()}")
            
            for oeuvre in oeuvres:
                if query.lower() in oeuvre.titre.lower() or (oeuvre.artiste and query.lower() in oeuvre.artiste.lower()) or (oeuvre.type_oeuvre and query.lower() in oeuvre.type_oeuvre.lower()):
                    # Image
                    image_url = None
                    try:
                        if hasattr(oeuvre, 'images') and oeuvre.images.exists():
                            image_url = oeuvre.images.first().image.url
                    except:
                        pass
                    
                    price = 75000  # Prix par défaut
                    try:
                        if hasattr(oeuvre, 'enchaireObjet') and oeuvre.enchaireObjet:
                            if oeuvre.enchaireObjet.price_reserved:
                                price = oeuvre.enchaireObjet.price_reserved
                    except:
                        pass
                    
                    name = oeuvre.titre
                    if oeuvre.artiste:
                        name = f"{oeuvre.titre} - {oeuvre.artiste}"
                    
                    # Nom d'enchère
                    auction_name = "Enchère non spécifiée"
                    try:
                        if hasattr(oeuvre, 'lot') and oeuvre.lot and hasattr(oeuvre.lot, 'enchaire') and oeuvre.lot.enchaire:
                            auction_name = oeuvre.lot.nom if hasattr(oeuvre.lot, 'nom') else f"Enchère #{oeuvre.lot.enchaire.id}"
                    except:
                        pass
                    
                    results.append({
                        'id': oeuvre.id,
                        'name': name,
                        'type': 'oeuvres_collections',
                        'category_name': 'Œuvres & Collections',
                        'auction_name': auction_name,
                        'price': price,
                        'image_url': image_url,
                        'ending_soon': False
                    })
                    print(f"Œuvre ajoutée: {name}")
        except Exception as e:
            print(f"Erreur œuvres: {e}")
    
    print(f"Total résultats: {len(results)}")
    return JsonResponse({'results': results[:10]})

@require_POST
@login_required
def change_pfp(request):
    user_id = request.POST.get('pfp')

@login_required
def favoris(request):
    user = request.user
    favoris = Enchaire.objects.filter(savers=user)

    for enchere in favoris:
        enchere.images = {
            'voitures': [],
            'immobiliers': [],
            'materiels': [],
            'informatique': [],
            'mobilier': [],
            'bijoux': [],
            'stocks': [],
            'oeuvres': [],
        }

        lot = enchere.lot
        all_images = []

        # Remplir images par catégorie
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

        for oeuvre in lot.oeuvres.all():
            for img in oeuvre.images.all():
                url = img.image.url
                enchere.images['oeuvres'].append(url)
                all_images.append(url)

        # Image principale aléatoire
        enchere.main_image_url = random.choice(all_images) if all_images else None

        # Récupérer tous les objets liés au lot pour récupérer les participations
        objets = []
        objets += list(lot.voitures.all())
        objets += list(lot.immobiliers.all())
        objets += list(lot.materiels.all())
        objets += list(lot.informatique.all())
        objets += list(lot.mobilier.all())
        objets += list(lot.bijoux.all())
        objets += list(lot.stocks.all())
        objets += list(lot.oeuvres.all())

        # Extraire les objets ayant un attribut enchaireObjet (sûr que tous les objets en ont ?)
        objets_avec_enchaire = [obj.enchaireObjet for obj in objets if hasattr(obj, 'enchaireObjet') and obj.enchaireObjet]

        # Récupérer les participations distinctes par user sur ces objets
        participations = ParticipationEnchaire.objects.filter(enchaireObjet__in=objets_avec_enchaire).values_list('user', flat=True).distinct()

        # Stocker le nombre de participants dans un attribut dynamique
        enchere.participant_count = participations.count()

    context = {
        'favoris': favoris,
        'user': user,
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

    return render(request, 'favoris/favoris.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

@require_POST
@login_required
def add_pfp(request):
    if 'profile_picture' not in request.FILES:
        messages.error(request, 'Aucun fichier sélectionné.')
        return redirect('profil')
    
    uploaded_file = request.FILES['profile_picture']
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if uploaded_file.content_type not in allowed_types:
        messages.error(request, 'Format de fichier non supporté. Utilisez JPG, PNG, GIF ou WebP.')
        return redirect('profil')
    
    # Validate file size (max 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    if uploaded_file.size > max_size:
        messages.error(request, 'Le fichier est trop volumineux. Taille maximale: 5MB.')
        return redirect('profil')
    
    try:
        # Remove old profile picture if exists
        if request.user.pfp:
            old_pfp_path = request.user.pfp.path
            if os.path.exists(old_pfp_path):
                os.remove(old_pfp_path)
        
        # Process and crop image to square
        image = Image.open(uploaded_file)
        
        # Convert to RGB if necessary (for PNG with transparency)
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        
        # Crop to square
        width, height = image.size
        size = min(width, height)
        
        # Calculate cropping coordinates (center crop)
        left = (width - size) // 2
        top = (height - size) // 2
        right = left + size
        bottom = top + size
        
        # Crop the image
        image = image.crop((left, top, right, bottom))
        
        # Resize to 400x400
        image = image.resize((400, 400), Image.Resampling.LANCZOS)
        
        # Save processed image
        output = BytesIO()
        image.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        # Create new file name
        file_extension = 'jpg'
        file_name = f'profile_pictures/{request.user.username}_{request.user.id}.{file_extension}'
        
        # Create InMemoryUploadedFile
        processed_file = InMemoryUploadedFile(
            output, 'ImageField', file_name, 'image/jpeg',
            sys.getsizeof(output), None
        )
        
        # Save to user profile
        request.user.pfp.save(file_name, processed_file, save=True)
        
        messages.success(request, 'Photo de profil mise à jour avec succès!')
        
    except Exception as e:
        messages.error(request, f'Erreur lors du traitement de l\'image: {str(e)}')
    
    return redirect('profil')

@login_required
def remove_pfp(request):
    try:
        if request.user.pfp:
            # Get the file path before deleting
            pfp_path = request.user.pfp.path
            
            # Remove the file from storage
            if os.path.exists(pfp_path):
                os.remove(pfp_path)
            
            # Clear the pfp field
            request.user.pfp.delete(save=False)
            request.user.pfp = None
            request.user.save()
            
            messages.success(request, 'Photo de profil supprimée avec succès!')
        else:
            messages.info(request, 'Aucune photo de profil à supprimer.')
            
    except Exception as e:
        messages.error(request, f'Erreur lors de la suppression: {str(e)}')
    
    return redirect('profil')

def faq(request):

    context = {}

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

    return render(request,'FAC.html',context)

def a_propos(request):

    context = {}

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

    return render(request,'a_propos.html',context)