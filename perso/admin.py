from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserAccount, EmailVerificationToken

class UserAccountAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'is_admin', 'is_active', 'email_verified_display')
    search_fields = ('email', 'username')
    readonly_fields = ('date_joined', 'last_login')
    list_filter = ('is_admin', 'is_active', 'email_verified')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('username', 'first_name', 'last_name', 'bio', 'pfp')}),
        ('Permissions', {'fields': ('is_admin', 'is_active', 'email_verified')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    ordering = ('email',)
    filter_horizontal = ()

    def email_verified_display(self, obj):
        return "✅" if obj.email_verified else "❌"
    email_verified_display.short_description = "Email vérifié"
    email_verified_display.admin_order_field = 'email_verified'

admin.site.register(UserAccount, UserAccountAdmin)
admin.site.register(EmailVerificationToken)



from django.contrib import admin
from Ezayd.models import (
    Enchaire, DemandeEnchaire, Lot,
    Voiture, VoitureImage,
    Immobilier, ImmobilierImage,
    MaterielProfessionnel, MaterielProfessionnelImage,
    InformatiqueElectronique, InformatiqueImage,
    MobilierEquipement
)

# ---------- Admin pour Enchaire ----------
@admin.register(Enchaire)
class EnchaireAdmin(admin.ModelAdmin):
    list_display = ('lot', 'seller', 'winner', 'etat', 'date_debut', 'date_fin',  'is_reserved')
    list_filter = ('etat',  'is_reserved', 'date_debut', 'date_fin')
    search_fields = ('lot__nom', 'seller__username', 'winner__username')
    readonly_fields = ('notified_users',)
    filter_horizontal = ('savers', 'notified_users')


# ---------- Admin pour DemandeEnchaire ----------
@admin.register(DemandeEnchaire)
class DemandeEnchaireAdmin(admin.ModelAdmin):
    list_display = ('enchaire', 'user', 'date', 'approved', 'seen', 'deleted')
    list_filter = ('approved', 'seen', 'deleted', 'date')
    search_fields = ('user__username', 'enchaire__lot__nom')


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
    list_display = ('titre', 'ville', 'type_bien', 'surface', 'prix', 'lot')
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

