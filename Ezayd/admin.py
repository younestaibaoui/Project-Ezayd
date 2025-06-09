from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.contrib import admin
from .models import (
    Enchaire, EnchaireObjet, DemandeEnchaire, ParticipationEnchaire,
    Lot, 
    Voiture, VoitureImage,
    Immobilier, ImmobilierImage,
    MaterielProfessionnel, MaterielProfessionnelImage,
    InformatiqueElectronique, InformatiqueImage,
    MobilierEquipement, MobilierImage,
    BijouxObjetValeur,BijouxImage
)


# ---------- Admin pour Enchaire ----------
@admin.register(Enchaire)
class EnchaireAdmin(admin.ModelAdmin):
    list_display = ('id','lot', 'seller', 'etat','wilaya' ,'date_debut', 'date_fin', 'is_active_display')
    list_filter = ('etat' ,'wilaya', 'date_debut', 'date_fin')
    search_fields = ('lot__nom', 'seller__username')
    readonly_fields = ('notified_users',)
    filter_horizontal = ('savers', 'notified_users')

    @admin.display(boolean=True, description='Active')
    def is_active_display(self, obj):
        return obj.is_active()



# ---------- Admin pour DemandeEnchaire ----------
@admin.register(DemandeEnchaire)
class DemandeEnchaireAdmin(admin.ModelAdmin):
    list_display = ('enchaire', 'user', 'date_demande', 'state')
    list_filter = ('state', 'date_demande')
    search_fields = ('user__username', 'enchaire__lot__nom')  # Ensure lot and nom exist

# ---------- Admin pour EnchaireObjet ----------
@admin.register(EnchaireObjet)
class EnchaireObjetAdmin(admin.ModelAdmin):
    list_display = ('objet_id','type', 'first_price', 'pas', 'price_reserved', 'winner')
    list_filter = ('objet_id',)
    search_fields = ('winner__username',)
    readonly_fields = ('objet_id', 'type',)

# ---------- Admin pour ParticipationEnchaire ----------
@admin.register(ParticipationEnchaire)
class ParticipationEnchaireAdmin(admin.ModelAdmin):
    list_display = ('enchaireObjet', 'user', 'date_participation')
    list_filter = ('date_participation',)
    search_fields = ('user__username', 'enchaireObjet__id')
    ordering = ('-date_participation',)


# ---------- Admin pour Lot ----------
@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type', 'date_ajout')
    list_filter = ('type',)
    search_fields = ('nom',)


# ---------- Admin pour Voiture et Images ----------
class VoitureImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        images = [form for form in self.forms if not form.cleaned_data.get('DELETE', False)]
        if len(images) < 3:
            raise ValidationError("Une voiture doit avoir au moins 3 images attachées.")

class VoitureImageInline(admin.TabularInline):
    model = VoitureImage
    formset = VoitureImageInlineFormSet
    extra = 3  # show at least 3 fields

@admin.register(Voiture)
class VoitureAdmin(admin.ModelAdmin):
    list_display = ('nom', 'model', 'year', 'lot')
    search_fields = ('nom', 'model', 'numero_chassis')
    list_filter = ('year', 'couleur')
    inlines = [VoitureImageInline]


# ---------- Admin pour Immobilier et Images ----------
class ImmobilierImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        images = [form for form in self.forms if not form.cleaned_data.get('DELETE', False)]
        if len(images) < 3:
            raise ValidationError("Une voiture doit avoir au moins 3 images attachées.")

class ImmobilierImageInline(admin.TabularInline):
    model = ImmobilierImage
    formset = ImmobilierImageInlineFormSet
    extra = 3  # show at least 3 fields

@admin.register(Immobilier)
class ImmobilierAdmin(admin.ModelAdmin):
    list_display = ('titre', 'ville', 'type_bien', 'surface', 'lot')
    search_fields = ('titre', 'ville', 'adresse')
    list_filter = ('type_bien', 'ville', 'garage', 'jardin', 'piscine')
    inlines = [ImmobilierImageInline]


# ---------- Admin pour MaterielProfessionnel et Images ----------
class MaterielProfessionnelImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        images = [form for form in self.forms if not form.cleaned_data.get('DELETE', False)]
        if len(images) < 3:
            raise ValidationError("Une voiture doit avoir au moins 3 images attachées.")

class MaterielProfessionnelImageInline(admin.TabularInline):
    model = MaterielProfessionnelImage
    formset = MaterielProfessionnelImageInlineFormSet
    extra = 3  # show at least 3 fields

@admin.register(MaterielProfessionnel)
class MaterielProfessionnelAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_materiel', 'marque', 'modele', 'annee_fabrication', 'disponibilite')
    list_filter = ('type_materiel', 'disponibilite')
    search_fields = ('nom', 'marque', 'modele')
    inlines = [MaterielProfessionnelImageInline]


# ---------- Admin pour InformatiqueElectronique et Images ----------
class InformatiqueElectroniqueImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        images = [form for form in self.forms if not form.cleaned_data.get('DELETE', False)]
        if len(images) < 3:
            raise ValidationError("Une voiture doit avoir au moins 3 images attachées.")

class InformatiqueElectroniqueImageInline(admin.TabularInline):
    model = InformatiqueImage
    formset = ImmobilierImageInlineFormSet
    extra = 3  # show at least 3 fields

@admin.register(InformatiqueElectronique)
class InformatiqueElectroniqueAdmin(admin.ModelAdmin):
    list_display = ('type_objet', 'marque', 'modele', 'annee', 'garantie')
    list_filter = ('type_objet', 'garantie')
    search_fields = ('marque', 'modele')
    inlines = [InformatiqueElectroniqueImageInline]


# ---------- Admin pour MobilierEquipement ----------
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from .models import MobilierEquipement, MobilierImage

# ❌ PAS DE DÉCORATEUR ICI !
class MobilierEquipementImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        images = [form for form in self.forms if not form.cleaned_data.get('DELETE', False)]
        if len(images) < 3:
            raise ValidationError("Un objet de type Mobilier & Équipement doit avoir au moins 3 images attachées.")

# Inline pour les images
class MobilierEquipementImageInline(admin.TabularInline):
    model = MobilierImage
    formset = MobilierEquipementImageInlineFormSet
    extra = 3  # Nombre de champs images affichés par défaut

# Admin pour MobilierEquipement
@admin.register(MobilierEquipement)
class MobilierEquipementAdmin(admin.ModelAdmin):
    list_display = ('categorie', 'materiau', 'couleur', 'lot')
    search_fields = ('categorie', 'materiau', 'couleur')
    inlines = [MobilierEquipementImageInline]


# ---------- Admin pour BijouxObjetValeur ----------
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

# FormSet avec validation : minimum 3 images
class BijouxImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        images = [form for form in self.forms if not form.cleaned_data.get('DELETE', False)]
        if len(images) < 3:
            raise ValidationError("Un bijou ou objet de valeur doit avoir au moins 3 images attachées.")

# Inline admin pour BijouxImage
class BijouxImageInline(admin.TabularInline):
    model = BijouxImage
    formset = BijouxImageInlineFormSet
    extra = 3  # au moins 3 champs d’image visibles

# Admin principal pour BijouxObjetValeur
@admin.register(BijouxObjetValeur)
class BijouxObjetValeurAdmin(admin.ModelAdmin):
    list_display = ('type_objet', 'matiere', 'poids', 'lot')  # noms des champs corrigés
    search_fields = ('type_objet', 'matiere')
    inlines = [BijouxImageInline]

