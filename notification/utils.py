from perso.models import UserAccount
from .models import NotificationDemandeEnchaire

def notify_admin(demande):
    admin_users = UserAccount.objects.filter(is_superuser=True)
    
    NotificationDemandeEnchaire.objects.create(
        user=demande.user,
        enchaire=demande.enchaire,
        message=f"Nouvelle demande d'enchère: {demande.enchaire} par {demande.user}",
        link=f"/admin/Ezayd/demandeenchaire/{demande.id}/change/"
    )
