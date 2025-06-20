from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from perso.models import UserAccount
from notification.models import NotificationEnchaire,NotificationDemandeEnchaire


# Liste des wilayas d'Algérie (exemple, à adapter si besoin)
WILAYAS_ALGERIE = [
    ('Adrar', 'Adrar'),
    ('Chlef', 'Chlef'),
    ('Laghouat', 'Laghouat'),
    ('Oum El Bouaghi', 'Oum El Bouaghi'),
    ('Batna', 'Batna'),
    ('Béjaïa', 'Béjaïa'),
    ('Biskra', 'Biskra'),
    ('Béchar', 'Béchar'),
    ('Blida', 'Blida'),
    ('Bouira', 'Bouira'),
    ('Tamanrasset', 'Tamanrasset'),
    ('Tébessa', 'Tébessa'),
    ('Tlemcen', 'Tlemcen'),
    ('Tiaret', 'Tiaret'),
    ('Tizi Ouzou', 'Tizi Ouzou'),
    ('Alger', 'Alger'),
    ('Djelfa', 'Djelfa'),
    ('Jijel', 'Jijel'),
    ('Sétif', 'Sétif'),
    ('Saïda', 'Saïda'),
    ('Skikda', 'Skikda'),
    ('Sidi Bel Abbès', 'Sidi Bel Abbès'),
    ('Annaba', 'Annaba'),
    ('Guelma', 'Guelma'),
    ('Constantine', 'Constantine'),
    ('Médéa', 'Médéa'),
    ('Mostaganem', 'Mostaganem'),
    ("M'Sila", "M'Sila"),
    ('Mascara', 'Mascara'),
    ('Ouargla', 'Ouargla'),
    ('Oran', 'Oran'),
    ('El Bayadh', 'El Bayadh'),
    ('Illizi', 'Illizi'),
    ('Bordj Bou Arreridj', 'Bordj Bou Arreridj'),
    ('Boumerdès', 'Boumerdès'),
    ('El Tarf', 'El Tarf'),
    ('Tindouf', 'Tindouf'),
    ('Tissemsilt', 'Tissemsilt'),
    ('El Oued', 'El Oued'),
    ('Khenchela', 'Khenchela'),
    ('Souk Ahras', 'Souk Ahras'),
    ('Tipaza', 'Tipaza'),
    ('Mila', 'Mila'),
    ('Aïn Defla', 'Aïn Defla'),
    ('Naâma', 'Naâma'),
    ('Aïn Témouchent', 'Aïn Témouchent'),
    ('Ghardaïa', 'Ghardaïa'),
    ('Relizane', 'Relizane'),
]

# ---------------------------------------- Auction Management ----------------------------------------
ETAT_ENCHAIRE_CHOICES = (
    ('upcoming', 'À venir'),
    ('active', 'En cours'),
    ('finis', 'Terminé'),
)


from django.db import models
from django.core.validators import MinValueValidator

class EnchaireObjet(models.Model):

    TYPE_CHOICES = [
        (None,'-'),
        ('vehicules', 'Véhicules'),
        ('immobilier', 'Immobilier'),
        ('materiel_pro', 'Matériel professionnel'),
        ('informatique_electronique', 'Informatique & électronique'),
        ('mobilier_equipements', 'Mobilier & équipements'),
        ('bijoux_objets_valeur', 'Bijoux & objets de valeur'),
        ('stocks_invendus', 'Stocks et invendus'),
        ('oeuvres_collections', 'Œuvres & collections'),
    ]

    first_price = models.IntegerField(null=False, validators=[MinValueValidator(0)])
    pas = models.IntegerField(null=False, validators=[MinValueValidator(0)])
    reserved = models.BooleanField(default=False)
    winner = models.ForeignKey(
        "perso.UserAccount",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price_reserved = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=30, null=True, blank=True, default=None,choices=TYPE_CHOICES)
    objet_id = models.IntegerField(null=True,blank=True,default=None)

    def save(self, *args, **kwargs):
        if self.pk is None and self.price_reserved is None:
            self.price_reserved = self.first_price - self.pas
        super().save(*args, **kwargs)        

    def participer(self, user):
        price_reserved = self.price_reserved 
        self.price_reserved = price_reserved + self.pas
        self.winner = user
        ParticipationEnchaire.objects.create(
            enchaireObjet=self,
            user=user,
            montant=self.price_reserved,
        )
        self.save()

    def get_objet(self):

        type_objet = self.type

        if type_objet == 'vehicules':
            objet = Voiture.objects.get(id=self.objet_id)
        elif type_objet == 'immobilier':
            objet = Immobilier.objects.get(id=self.objet_id)
        elif type_objet == 'materiel_pro':
            objet = MaterielProfessionnel.objects.get(id=self.objet_id)
        elif type_objet == 'informatique_electronique':
            objet = InformatiqueElectronique.objects.get(id=self.objet_id)
        elif type_objet == 'mobilier_equipements':
            objet = MobilierEquipement.objects.get(id=self.objet_id)
        elif type_objet == 'bijoux_objets_valeur':
            objet = BijouxObjetValeur.objects.get(id=self.objet_id)
        elif type_objet == 'stocks_invendus':
            objet = StockInvendu.objects.get(id=self.objet_id)
        elif type_objet == 'oeuvres_collections':
            objet = OeuvreCollection.objects.get(id=self.objet_id)
        else:
            objet = None

        return objet

    def __str__(self):
        try:
            objet = self.get_objet()
        except:
            objet = f"EnchaireObjet #{self.id} (sans objet)"

        return str(objet) 
    
class Enchaire(models.Model):
    date_debut = models.DateField(default=timezone.now, null=False)
    date_fin = models.DateField(default=timezone.now, null=False)
    
    seller = models.ForeignKey(
        "perso.UserAccount",
        null=False,
        on_delete=models.CASCADE,
        related_name="enchaires_proprietes"
    )

    etat = models.CharField(
        choices=ETAT_ENCHAIRE_CHOICES,
        max_length=10,
        default='upcoming'
    )

    savers = models.ManyToManyField(
        "perso.UserAccount",
        related_name='enchaires_saved',
        blank=True
    )

    wilaya = models.CharField(
        max_length=50,
        choices=WILAYAS_ALGERIE,
        default='Alger',
        null=True,
        blank=True,
        help_text="Wilaya de l'enchère"
    )

    def __str__(self):
        return str(self.lot.nom) if hasattr(self, 'lot') else f"Enchaire #{self.id} (sans lot)"


    def calculer_etat_auto(self):
        today = timezone.now().date()
        if today < self.date_debut:
            return 'upcoming'
        elif self.date_debut <= today < self.date_fin:
            return 'active'
        else:
            type_objet = self.lot.type

            if type_objet == 'vehicules':
                EnchaireObjet.objects.filter(voiture__lot__enchaire=self).update(reserved=True)
            elif type_objet == 'immobilier':
                EnchaireObjet.objects.filter(immobilier__lot__enchaire=self).update(reserved=True)
            elif type_objet == 'materiel_pro':
                EnchaireObjet.objects.filter(materielProfessionnel__lot__enchaire=self).update(reserved=True)
            elif type_objet == 'informatique_electronique':
                EnchaireObjet.objects.filter(informatiqueElectronique__lot__enchaire=self).update(reserved=True)
            elif type_objet == 'mobilier_equipements':
                EnchaireObjet.objects.filter(mobilierEquipement__lot__enchaire=self).update(reserved=True)
            elif type_objet == 'bijoux_objets_valeur':
                EnchaireObjet.objects.filter(bijouxObjetValeur__lot__enchaire=self).update(reserved=True)
            elif type_objet == 'stocks_invendus':
                EnchaireObjet.objects.filter(stockInvendu__lot__enchaire=self).update(reserved=True)
            elif type_objet == 'oeuvres_collections':
                EnchaireObjet.objects.filter(oeuvreCollection__lot__enchaire=self).update(reserved=True)
        
            return 'finis'

    def save(self, *args, **kwargs):
        new_etat = self.calculer_etat_auto()
        if self.pk:
            old_etat = Enchaire.objects.get(pk=self.pk).etat
            if old_etat != new_etat:
                self.etat = new_etat
                super().save(*args, **kwargs)
                self.notify_savers(old_etat)
                return
        self.etat = new_etat
        super().save(*args, **kwargs)

    # methode pour notifier les utilisateur de changement d'etat
    def notify_savers(self, old_etat):

        if old_etat == 'upcoming':
            message = "L’enchère vient de commencer — ne manquez pas votre chance de faire la meilleure offre !"
        else:
            message = "L’enchère est maintenant terminée !"

        for user in self.savers.all():
            NotificationEnchaire.objects.create(
                user=user,
                enchaire=self,
                message=message,
            )

    def is_active(self):
        return True if self.etat == 'active' else False

    class Meta:
        indexes = [
            models.Index(fields=["etat"]),
            models.Index(fields=["date_debut", "date_fin"]),
        ]

# ---------------------------------------- DEMANDE ENCHERE ----------------------------------------
class DemandeEnchaire(models.Model):
    class State(models.TextChoices):
        UNREAD = 'unread', 'Non lu'
        APPROVED = 'Approuvée', 'Approuvée'
        REJECTED = 'Rejetée', 'Rejetée'

    enchaire = models.ForeignKey(
        "Enchaire",
        null=False,
        on_delete=models.CASCADE,
        related_name="demande"
    )

    user = models.ForeignKey(
        "perso.UserAccount",
        on_delete=models.CASCADE,
        related_name="demandes_enchaire"
    )

    date_demande = models.DateTimeField(default=timezone.now)
    date_accepte = models.DateTimeField(blank=True, null=True)
    state = models.CharField(
        max_length=10,
        choices=State.choices,
        default=State.UNREAD
    )

    def save(self, *args, **kwargs):
        # Detect if etat has changed
        if self.pk:  # object already exists
            if self.state != self.State.UNREAD:
                super().save(*args, **kwargs)  # save first to ensure FK integrity
                self.notify_user(self.state,self.user,self.enchaire)
                self.delete_notif(self.user,self.enchaire)
                 
        super().save(*args, **kwargs)

    def notify_user(self, new_etat, user ,enchaire):

        if new_etat == 'Approuvée':
            if enchaire.is_active():
                message = "Votre demande de participation a été approuvée, vous pouvez enchérir maintenant !"
            else:
                message = "Votre demande de réservation a été approuvée, vous pouvez enchérir dès que l'enchère s’ouvre."
        else:
            if enchaire.is_active():
                message = "Votre demande de participation a été rejetée"
            else:
                message = "Votre demande de réservation a été rejetée."

        NotificationEnchaire.objects.create(
            user=user,
            enchaire=enchaire,
            message=message,
        )
    
    def delete_notif(self, user, enchaire):
        try:
            notification = NotificationDemandeEnchaire.objects.filter(
                user=user,
                enchaire=enchaire,  
            ).first()
            notification.delete()
        except NotificationDemandeEnchaire.DoesNotExist:
            pass 

    def __str__(self):
        return f"Demande de l'enchère '{self.enchaire}'"

    def get_absolute_url(self):
        return reverse('demande_enchaire_detail', args=[self.pk])
 
# ---------------------------------------- PARTICIPATION ENCHERE ----------------------------------------
class ParticipationEnchaire(models.Model):
    enchaireObjet = models.ForeignKey(
        "EnchaireObjet",
        on_delete=models.CASCADE,
        related_name="participations"
    )

    user = models.ForeignKey(
        "perso.UserAccount",
        on_delete=models.CASCADE,
        related_name="participations_encheres"
    )
    
    montant = models.IntegerField(
        null=False,
        validators=[MinValueValidator(0)],
        help_text="Montant de la participation",
        default=0,
    )
    date_participation = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        users = ParticipationEnchaire.objects.filter(enchaireObjet=self.enchaireObjet).values('user').distinct()
        super().save(*args, **kwargs)  # save first to ensure FK integrity
        for user in users:
            if user['user'] == self.user.id:
                continue  # Skip if the user already exists in the participation list

            self.notify_user(self.montant,user,self.enchaireObjet)

    def notify_user(self, montant, user ,enchaireObjet):
        NotificationEnchaire.objects.create(
            user=UserAccount.objects.get(id=user['user']),
            enchaireObjet=enchaireObjet,
            message=f"Un autre utilisateur a proposé un montant supérieur au vôtre dans l'enchère."
        )

    def __str__(self):
        return f"Participation de {self.user} à l'enchère {self.enchaireObjet}."

# ----------------------------------------LOTS -----------------------------------------------

class Lot(models.Model):
    TYPE_CHOICES = [
        ('vehicules', 'Véhicules'),
        ('immobilier', 'Immobilier'),
        ('materiel_pro', 'Matériel professionnel'),
        ('informatique_electronique', 'Informatique & électronique'),
        ('mobilier_equipements', 'Mobilier & équipements'),
        ('bijoux_objets_valeur', 'Bijoux & objets de valeur'),
        ('stocks_invendus', 'Stocks et invendus'),
        ('oeuvres_collections', 'Œuvres & collections'),
    ]

    nom = models.CharField(max_length=100, null=False)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    description = models.TextField(null=True, blank=True, max_length=150)
    date_ajout = models.DateTimeField(auto_now_add=True)
    enchaire = models.OneToOneField(
        "Enchaire",
        related_name="lot",
        null=False,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.nom
    
# -------------------------------------- CARS -------------------------------------
class Voiture(models.Model):
    lot = models.ForeignKey(Lot, related_name='voitures', on_delete=models.CASCADE)
    nom = models.CharField(max_length=20, null=False)
    model = models.CharField(max_length=20, null=False)
    year = models.IntegerField(default=datetime.now().year, null=False)
    numero_chassis = models.CharField(max_length=20, null=True)
    etat = models.IntegerField(null=True)
    couleur = models.CharField(max_length=20, null=True)
    details = models.TextField()
    youtube_video = models.URLField(null=True, blank=True)
    climatiseur = models.BooleanField(default=False)
    gps_navigation = models.BooleanField(default=False)
    toit_ouvrant = models.BooleanField(default=False)
    sieges_ventiles = models.BooleanField(default=False)
    camera_recul = models.BooleanField(default=False)
    capteurs_stationnement = models.BooleanField(default=False)
    regulateur_vitesse = models.BooleanField(default=False)
    regulateur_vitesse_adaptatif = models.BooleanField(default=False)
    enchaireObjet = models.OneToOneField(
        "EnchaireObjet",
        related_name="voiture",
        null=False,
        on_delete=models.CASCADE,
    )

    def get_images(self):
        return [img.image.url for img in self.images.all()]

    def clean(self):
        # S'assurer que le lot est de type 'vehicules'
        if self.lot and self.lot.type != 'vehicules':
            raise ValidationError("Une voiture ne peut être liée qu'à un lot de type 'Véhicules'.")

    def update_enchaireObjet(self):
        enchaireObjet = self.enchaireObjet
        enchaireObjet.type = self.lot.type
        enchaireObjet.objet_id = self.id
        enchaireObjet.save()

    def save(self, *args, **kwargs):
        self.full_clean()  # Appelle clean() et lève une exception si invalide
        super().save(*args, **kwargs)
        self.update_enchaireObjet()

    def __str__(self):
        return f"{self.nom}-{self.model}-{self.year}" if self.pk else "Objet supprimé ou introuvable"

class VoitureImage(models.Model):
    type=(
        ('1','main_image'),
        ('2','side_image'),
        ('3','inside_image'),
        ('4','engine_image'),
        ('5','additional_image'),
        ('6','main_side_image'),
        ('7','main_inside_image'),
        ('8','main_engine_image'),
        ('9','registrations_paper_image'),
    )
    voiture = models.ForeignKey("Voiture", related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(null=False,upload_to='images/')
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(choices=type,default='5',max_length=20)
    def __str__(self):
        upload_time = self.date.strftime('%Y-%m-%d at %H:%M:%S')
        return f"Image of '{self.voiture}' uploaded at {upload_time}"

# -------------------------------------- Immobilier -------------------------------------
class Immobilier(models.Model):
    TYPE_IMMO_CHOICES = [
        ('habitation', 'Habitations'),
        ('locaux_commerciaux', 'Locaux commerciaux'),
        ('terrain', 'Terrains'),
    ]

    lot = models.ForeignKey("Lot", related_name="immobiliers", on_delete=models.CASCADE)
    titre = models.CharField(max_length=100)
    type_bien = models.CharField(max_length=30, choices=TYPE_IMMO_CHOICES)
    surface = models.FloatField(help_text="Surface en m²")
    adresse = models.TextField()
    ville = models.CharField(max_length=50)
    code_postal = models.CharField(max_length=10)
    description = models.TextField()
    nombre_pieces = models.IntegerField(null=True, blank=True)
    nombre_chambres = models.IntegerField(null=True, blank=True)
    salle_de_bain = models.IntegerField(null=True, blank=True)
    garage = models.BooleanField(default=False)
    jardin = models.BooleanField(default=False)
    piscine = models.BooleanField(default=False)
    date_construction = models.DateField(null=True, blank=True)
    enchaireObjet = models.OneToOneField(
        "EnchaireObjet",
        related_name="immobilier",
        null=False,
        on_delete=models.CASCADE
    )

    def get_images(self):
        return [img.image.url for img in self.images.all()]

    def clean(self):
        if self.lot and self.lot.type != 'immobilier':
            raise ValidationError("Un bien immobilier doit appartenir à un lot de type 'Immobilier'.")

    def update_enchaireObjet(self):
        enchaireObjet = self.enchaireObjet
        enchaireObjet.type = self.lot.type
        enchaireObjet.objet_id = self.id
        enchaireObjet.save()
        
    def save(self, *args, **kwargs):
        self.full_clean()  # Appelle clean() et lève une exception si invalide
        self.update_enchaireObjet()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.titre} - {self.ville}"
class ImmobilierImage(models.Model):
    TYPE_IMAGE_CHOICES = [
        ('1', 'main_image'),
        ('2', 'interior_image'),
        ('3', 'exterior_image'),
        ('4', 'floor_plan'),
        ('5', 'additional_image'),
    ]

    immobilier = models.ForeignKey(Immobilier, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='immobilier/')
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(choices=TYPE_IMAGE_CHOICES, default='5', max_length=20)

    def __str__(self):
        return f"Image of '{self.immobilier}' uploaded at {self.date.strftime('%Y-%m-%d %H:%M:%S')}"

# -------------------------------------- Matériel professionnel -------------------------------------

class MaterielProfessionnel(models.Model):
    TYPE_MATERIEL_CHOICES = [
        ('machines_equipements', 'Machines & équipements'),
        ('engins_chantier', 'Engins de chantier'),
        ('materiel_agricole', 'Matériel agricole'),
    ]

    lot = models.ForeignKey("Lot", related_name="materiels", on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    type_materiel = models.CharField(max_length=30, choices=TYPE_MATERIEL_CHOICES)
    marque = models.CharField(max_length=50, null=True, blank=True)
    modele = models.CharField(max_length=50, null=True, blank=True)
    annee_fabrication = models.IntegerField(null=True, blank=True)
    etat = models.CharField(max_length=100, null=True, blank=True)
    puissance = models.CharField(max_length=50, null=True, blank=True)
    poids = models.FloatField(null=True, blank=True, help_text="Poids en kg")
    description = models.TextField()
    disponibilite = models.BooleanField(default=True)
    enchaireObjet = models.OneToOneField(
        "EnchaireObjet",
        related_name="materielProfessionnel",
        null=False,
        on_delete=models.CASCADE
    )

    def get_images(self):
        return [img.image.url for img in self.images.all()]

    def clean(self):
        if self.lot and self.lot.type != 'materiel_pro':
            raise ValidationError("Le matériel professionnel doit appartenir à un lot de type 'Matériel professionnel'.")

    def update_enchaireObjet(self):
        enchaireObjet = self.enchaireObjet
        enchaireObjet.type = self.lot.type
        enchaireObjet.objet_id = self.id
        enchaireObjet.save()
        
    def save(self, *args, **kwargs):
        self.full_clean()  # Appelle clean() et lève une exception si invalide
        self.update_enchaireObjet()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.nom} ({self.type_materiel})"

class MaterielProfessionnelImage(models.Model):
    TYPE_IMAGE_CHOICES = [
        ('1', 'main_image'),
        ('2', 'detail_image'),
        ('3', 'usage_image'),
        ('4', 'technical_sheet'),
        ('5', 'additional_image'),
    ]

    materiel = models.ForeignKey(MaterielProfessionnel, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='materiel_pro/')
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(choices=TYPE_IMAGE_CHOICES, default='5', max_length=20)

    def __str__(self):
        return f"Image of '{self.materiel}' uploaded at {self.date.strftime('%Y-%m-%d %H:%M:%S')}"

# -------------------------------------- Informatique & électronique -------------------------------------
class InformatiqueElectronique(models.Model):
    TYPE_CHOICES = [
        ('ordinateur', 'Ordinateur'),
        ('telephone', 'Téléphone'),
        ('tv_audio', 'TV / Audio'),
        ('autre', 'Autre'),
    ]

    lot = models.ForeignKey(Lot, related_name='informatique', on_delete=models.CASCADE)
    type_objet = models.CharField(max_length=30, choices=TYPE_CHOICES)
    marque = models.CharField(max_length=50, null=True, blank=True)
    modele = models.CharField(max_length=50, null=True, blank=True)
    annee = models.IntegerField(null=True, blank=True)
    description = models.TextField()
    etat = models.CharField(max_length=100, null=True, blank=True)
    garantie = models.BooleanField(default=False)
    enchaireObjet = models.OneToOneField(
        "EnchaireObjet",
        related_name="informatiqueElectronique",
        null=False,
        on_delete=models.CASCADE
    )

    def get_images(self):
        return [img.image.url for img in self.images.all()]

    def clean(self):
        if self.lot.type != 'informatique_electronique':
            raise ValidationError("Ce produit doit appartenir à un lot de type 'Informatique & électronique'.")

    def update_enchaireObjet(self):
        enchaireObjet = self.enchaireObjet
        enchaireObjet.type = self.lot.type
        enchaireObjet.objet_id = self.id
        enchaireObjet.save()
        
    def save(self, *args, **kwargs):
        self.full_clean()  # Appelle clean() et lève une exception si invalide
        self.update_enchaireObjet()
        super().save(*args, **kwargs)


    def __str__(self):
        parts = []
        if self.marque:
            parts.append(self.marque)
        if self.modele:
            parts.append(self.modele)
        if self.type_objet:
            parts.append(f"({self.get_type_objet_display()})")  # Affiche le label lisible du choix
        return " ".join(parts) if parts else f"Informatique #{self.id}"


class InformatiqueImage(models.Model):
    objet = models.ForeignKey(InformatiqueElectronique, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='informatique/')
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=30, default='photo')  # Ex: écran, boîtier, etc.

    def __str__(self):
        return f"Image de {self.objet.marque} - {self.date.strftime('%Y-%m-%d')}"

# -------------------------------------- Mobilier & équipements -------------------------------------
class MobilierEquipement(models.Model):
    lot = models.ForeignKey(Lot, related_name='mobilier', on_delete=models.CASCADE)
    categorie = models.CharField(max_length=100)
    materiau = models.CharField(max_length=50, null=True, blank=True)
    couleur = models.CharField(max_length=50, null=True, blank=True)
    dimensions = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField()
    etat = models.CharField(max_length=100, null=True, blank=True)
    enchaireObjet = models.OneToOneField(
        "EnchaireObjet",
        related_name="mobilierEquipement",
        null=False,
        on_delete=models.CASCADE
    )

    def get_images(self):
        return [img.image.url for img in self.images.all()]

    def clean(self):
        if self.lot.type != 'mobilier_equipements':
            raise ValidationError("Cet objet doit appartenir à un lot de type 'Mobilier & équipements'.")

    def update_enchaireObjet(self):
        enchaireObjet = self.enchaireObjet
        enchaireObjet.type = self.lot.type
        enchaireObjet.objet_id = self.id
        enchaireObjet.save()
        
    def save(self, *args, **kwargs):
        self.full_clean()  # Appelle clean() et lève une exception si invalide
        self.update_enchaireObjet()
        super().save(*args, **kwargs)


class MobilierImage(models.Model):
    mobilier = models.ForeignKey(MobilierEquipement, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='mobilier/')
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=30, default='photo')  # Ex: face, profil, détail

    def __str__(self):
        return f"Image du mobilier {self.mobilier.categorie} - {self.date.strftime('%Y-%m-%d')}"

# -------------------------------------- Bijoux & objets de valeur -------------------------------------

class BijouxObjetValeur(models.Model):
    lot = models.ForeignKey(Lot, related_name='bijoux', on_delete=models.CASCADE)
    type_objet = models.CharField(max_length=100)
    matiere = models.CharField(max_length=50)
    poids = models.FloatField(help_text="Poids en grammes")
    carats = models.IntegerField(null=True, blank=True)
    description = models.TextField()
    enchaireObjet = models.OneToOneField(
        "EnchaireObjet",
        related_name="bijouxObjetValeur",
        null=False,
        on_delete=models.CASCADE
    )

    def get_images(self):
        return [img.image.url for img in self.images.all()]
    
    def clean(self):
        if self.lot.type != 'bijoux_objets_valeur':
            raise ValidationError("Cet objet doit appartenir à un lot de type 'Bijoux & objets de valeur'.")

    def update_enchaireObjet(self):
        enchaireObjet = self.enchaireObjet
        enchaireObjet.type = self.lot.type
        enchaireObjet.objet_id = self.id
        enchaireObjet.save()
        
    def save(self, *args, **kwargs):
        self.full_clean()  # Appelle clean() et lève une exception si invalide
        self.update_enchaireObjet()
        super().save(*args, **kwargs)


class BijouxImage(models.Model):
    bijou = models.ForeignKey(BijouxObjetValeur, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='bijoux/')
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=30, default='photo')  # Ex: vue générale, détail

    def __str__(self):
        return f"Image de {self.bijou.type_objet} - {self.date.strftime('%Y-%m-%d')}"


# --------------------------------------- Stocks et invendus-------------------------------------
class StockInvendu(models.Model):
    lot = models.ForeignKey(Lot, related_name='stocks', on_delete=models.CASCADE)
    nom_produit = models.CharField(max_length=100)
    quantite = models.IntegerField()
    unite = models.CharField(max_length=20, default="pièces")
    description = models.TextField()
    enchaireObjet = models.OneToOneField(
        "EnchaireObjet",
        related_name="stockInvendu",
        null=False,
        on_delete=models.CASCADE
    )

    def get_images(self):
        return [img.image.url for img in self.images.all()]

    def clean(self):
        if self.lot.type != 'stocks_invendus':
            raise ValidationError("Ce produit doit appartenir à un lot de type 'Stocks et invendus'.")

    def update_enchaireObjet(self):
        enchaireObjet = self.enchaireObjet
        enchaireObjet.type = self.lot.type
        enchaireObjet.objet_id = self.id
        enchaireObjet.save()
        
    def save(self, *args, **kwargs):
        self.full_clean()  # Appelle clean() et lève une exception si invalide
        self.update_enchaireObjet()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nom_produit


class StockImage(models.Model):
    produit = models.ForeignKey(StockInvendu, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='stocks/')
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=30, default='photo')  # Ex: emballage, détail, palette

    def __str__(self):
        return f"Image du stock {self.produit.nom_produit} - {self.date.strftime('%Y-%m-%d')}"

# --------------------------------------- Œuvres & collections -------------------------------------
class OeuvreCollection(models.Model):
    lot = models.ForeignKey(Lot, related_name='oeuvres', on_delete=models.CASCADE)
    titre = models.CharField(max_length=200)
    artiste = models.CharField(max_length=100, null=True, blank=True)
    annee_creation = models.IntegerField(null=True, blank=True)
    type_oeuvre = models.CharField(max_length=100)
    dimensions = models.CharField(max_length=100, null=True, blank=True)
    technique = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField()
    enchaireObjet = models.OneToOneField(
        "EnchaireObjet",
        related_name="oeuvreCollection",
        null=False,
        on_delete=models.CASCADE
    )

    def get_images(self):
        return [img.image.url for img in self.images.all()]

    def clean(self):
        if self.lot.type != 'oeuvres_collections':
            raise ValidationError("Cette œuvre doit appartenir à un lot de type 'Œuvres & collections'.")

    def update_enchaireObjet(self):
        enchaireObjet = self.enchaireObjet
        enchaireObjet.type = self.lot.type
        enchaireObjet.objet_id = self.id
        enchaireObjet.save()
        
    def save(self, *args, **kwargs):
        self.full_clean()  # Appelle clean() et lève une exception si invalide
        self.update_enchaireObjet()
        super().save(*args, **kwargs)


class OeuvreImage(models.Model):
    oeuvre = models.ForeignKey(OeuvreCollection, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='oeuvres/')
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=30, default='photo')  # Ex: vue complète, signature

    def __str__(self):
        return f"Image de l’œuvre '{self.oeuvre.titre}' - {self.date.strftime('%Y-%m-%d')}"

