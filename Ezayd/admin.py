from django.contrib import admin
from .models import (
    Enchaire, DemandeEnchaire, Lot,
    Voiture, VoitureImage,
    Immobilier, ImmobilierImage,
    MaterielProfessionnel, MaterielProfessionnelImage,
    InformatiqueElectronique, InformatiqueImage,
    MobilierEquipement,
    EnchaireObjet, ParticipationEnchaire,
)


# ---------- Admin pour Enchaire ----------
@admin.register(Enchaire)
class EnchaireAdmin(admin.ModelAdmin):
    list_display = ('id','lot', 'seller', 'etat', 'date_debut', 'date_fin', 'is_active_display')
    list_filter = ('etat', 'date_debut', 'date_fin')
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
    list_display = ('id', 'first_price', 'pas', 'price_reserved', 'winner')
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
class VoitureImageInline(admin.TabularInline):
    model = VoitureImage
    extra = 1

@admin.register(Voiture)
class VoitureAdmin(admin.ModelAdmin):
    list_display = ('nom', 'model', 'year', 'lot')
    search_fields = ('nom', 'model', 'numero_chassis')
    list_filter = ('year', 'couleur')
    inlines = [VoitureImageInline]


# ---------- Admin pour Immobilier et Images ----------
class ImmobilierImageInline(admin.TabularInline):
    model = ImmobilierImage
    extra = 1

@admin.register(Immobilier)
class ImmobilierAdmin(admin.ModelAdmin):
    list_display = ('titre', 'ville', 'type_bien', 'surface', 'lot')
    search_fields = ('titre', 'ville', 'adresse')
    list_filter = ('type_bien', 'ville', 'garage', 'jardin', 'piscine')
    inlines = [ImmobilierImageInline]


# ---------- Admin pour MaterielProfessionnel et Images ----------
class MaterielProfessionnelImageInline(admin.TabularInline):
    model = MaterielProfessionnelImage
    extra = 1

@admin.register(MaterielProfessionnel)
class MaterielProfessionnelAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_materiel', 'marque', 'modele', 'annee_fabrication', 'disponibilite')
    list_filter = ('type_materiel', 'disponibilite')
    search_fields = ('nom', 'marque', 'modele')
    inlines = [MaterielProfessionnelImageInline]


# ---------- Admin pour InformatiqueElectronique et Images ----------
class InformatiqueImageInline(admin.TabularInline):
    model = InformatiqueImage
    extra = 1

@admin.register(InformatiqueElectronique)
class InformatiqueElectroniqueAdmin(admin.ModelAdmin):
    list_display = ('type_objet', 'marque', 'modele', 'annee', 'garantie')
    list_filter = ('type_objet', 'garantie')
    search_fields = ('marque', 'modele')
    inlines = [InformatiqueImageInline]


# ---------- Admin pour MobilierEquipement ----------
@admin.register(MobilierEquipement)
class MobilierEquipementAdmin(admin.ModelAdmin):
    list_display = ('categorie', 'materiau', 'couleur', 'lot')
    search_fields = ('categorie', 'materiau', 'couleur')


