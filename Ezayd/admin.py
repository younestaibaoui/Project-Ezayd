from django.contrib import admin
from .models import (
    Enchaire, DemandeEnchaire, EnchaireObjet, ParticipationEnchaire,
    Lot,
    Voiture, VoitureImage,
    Immobilier, ImmobilierImage,
    MaterielProfessionnel, MaterielProfessionnelImage,
    InformatiqueElectronique, InformatiqueImage,
    MobilierEquipement, MobilierImage,
    BijouxObjetValeur, BijouxImage,
    StockInvendu, StockImage,
    OeuvreCollection, OeuvreImage
)


# ---------- Admin pour Enchaire ----------
@admin.register(Enchaire)
class EnchaireAdmin(admin.ModelAdmin):
    list_display = ('id','lot', 'seller', 'etat', 'date_debut', 'date_fin', 'is_active_display')
    list_filter = ('etat', 'date_debut', 'date_fin')
    search_fields = ('lot__nom', 'seller__username')
    readonly_fields = ('etat',)
    filter_horizontal = ('savers',)

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
    list_display = ('__str__', 'first_price', 'pas', 'price_reserved', 'winner')
    list_filter = ('winner',)
    search_fields = ('winner__username',)

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
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

class VoitureImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        count = 0
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False) and form.cleaned_data:
                count += 1
        if count < 3:
            raise ValidationError("Vous devez ajouter au moins 3 images pour chaque voiture.")

class VoitureImageInline(admin.TabularInline):
    model = VoitureImage
    extra = 1
    formset = VoitureImageInlineFormSet


@admin.register(Voiture)
class VoitureAdmin(admin.ModelAdmin):
    list_display = ('id','nom', 'model', 'year', 'lot')
    search_fields = ('nom', 'model', 'numero_chassis')
    list_filter = ('year', 'couleur')
    inlines = [VoitureImageInline]


# ---------- Admin pour Immobilier et Images ----------
class ImmobilierImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        count = 0
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False) and form.cleaned_data:
                count += 1
        if count < 3:
            raise ValidationError("Vous devez ajouter au moins 3 images pour chaque bien immobilier.")

class ImmobilierImageInline(admin.TabularInline):
    model = ImmobilierImage
    extra = 1
    formset = ImmobilierImageInlineFormSet

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
        count = 0
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False) and form.cleaned_data:
                count += 1
        if count < 3:
            raise ValidationError("Vous devez ajouter au moins 3 images pour chaque matériel professionnel.")

class MaterielProfessionnelImageInline(admin.TabularInline):
    model = MaterielProfessionnelImage
    extra = 1
    formset = MaterielProfessionnelImageInlineFormSet

@admin.register(MaterielProfessionnel)
class MaterielProfessionnelAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_materiel', 'marque', 'modele', 'annee_fabrication', 'disponibilite')
    list_filter = ('type_materiel', 'disponibilite')
    search_fields = ('nom', 'marque', 'modele')
    inlines = [MaterielProfessionnelImageInline]


# ---------- Admin pour InformatiqueElectronique et Images ----------
class InformatiqueImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        count = 0
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False) and form.cleaned_data:
                count += 1
        if count < 3:
            raise ValidationError("Vous devez ajouter au moins 3 images pour chaque équipement informatique.")

class InformatiqueImageInline(admin.TabularInline):
    model = InformatiqueImage
    extra = 1
    formset = InformatiqueImageInlineFormSet

@admin.register(InformatiqueElectronique)
class InformatiqueElectroniqueAdmin(admin.ModelAdmin):
    list_display = ('type_objet', 'marque', 'modele', 'annee', 'garantie')
    list_filter = ('type_objet', 'garantie')
    search_fields = ('marque', 'modele')
    inlines = [InformatiqueImageInline]


# ---------- Admin pour MobilierEquipement ----------
# --- Formset personnalisé pour valider le nombre d'images ---
class MobilierImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        count = 0
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False) and form.cleaned_data:
                count += 1
        if count < 3:
            raise ValidationError("Vous devez ajouter au moins 3 images pour chaque mobilier.")

# --- Inline admin pour les images ---
class MobilierImageInline(admin.TabularInline):
    model = MobilierImage
    extra = 1
    formset = MobilierImageInlineFormSet

# --- Admin principal pour MobilierEquipement ---
@admin.register(MobilierEquipement)
class MobilierEquipementAdmin(admin.ModelAdmin):
    list_display = ('categorie', 'materiau', 'couleur', 'etat')
    search_fields = ('categorie', 'description')
    inlines = [MobilierImageInline]

# ---------- Admin pour BijouxObjetValeur ----------

# --- Formset personnalisé pour valider le nombre d'images ---
class BijouxImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        count = 0
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False) and form.cleaned_data:
                count += 1
        if count < 3:
            raise ValidationError("Vous devez ajouter au moins 3 images pour chaque bijou ou objet de valeur.")

# --- Inline admin pour les images de bijoux ---
class BijouxImageInline(admin.TabularInline):
    model = BijouxImage
    extra = 1
    formset = BijouxImageInlineFormSet

# --- Admin principal pour BijouxObjetValeur ---
@admin.register(BijouxObjetValeur)
class BijouxObjetValeurAdmin(admin.ModelAdmin):
    list_display = ('type_objet', 'matiere', 'poids', 'carats')
    search_fields = ('type_objet', 'matiere', 'description')
    inlines = [BijouxImageInline]

# --- Formset personnalisé pour valider le nombre d'images ---
class StockImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        count = 0
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False) and form.cleaned_data:
                count += 1
        if count < 3:
            raise ValidationError("Vous devez ajouter au moins 3 images pour chaque produit en stock.")

# --- Inline admin pour les images de stock ---
class StockImageInline(admin.TabularInline):
    model = StockImage
    extra = 1
    formset = StockImageInlineFormSet

# --- Admin principal pour StockInvendu ---
@admin.register(StockInvendu)
class StockInvenduAdmin(admin.ModelAdmin):
    list_display = ('nom_produit', 'quantite', 'unite')
    search_fields = ('nom_produit', 'description')
    inlines = [StockImageInline]

# --- Formset personnalisé pour valider le nombre d'images ---
class OeuvreImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        count = 0
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False) and form.cleaned_data:
                count += 1
        if count < 3:
            raise ValidationError("Vous devez ajouter au moins 3 images pour chaque œuvre.")

# --- Inline admin pour les images d'œuvres ---
class OeuvreImageInline(admin.TabularInline):
    model = OeuvreImage
    extra = 1
    formset = OeuvreImageInlineFormSet

# --- Admin principal pour OeuvreCollection ---
@admin.register(OeuvreCollection)
class OeuvreCollectionAdmin(admin.ModelAdmin):
    list_display = ('titre', 'artiste', 'annee_creation', 'type_oeuvre')
    search_fields = ('titre', 'artiste', 'description')
    inlines = [OeuvreImageInline]