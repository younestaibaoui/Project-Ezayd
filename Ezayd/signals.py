# to send signals for notifications to notify admin!!
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DemandeEnchaire
from notification.utils import notify_admin  

@receiver(post_save, sender=DemandeEnchaire)
def notify_admin_on_new_demande(sender, instance, created, **kwargs):
    if created:
        notify_admin(instance)
