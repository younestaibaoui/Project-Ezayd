# to add the number of unread notifications to the context of the admin
from .models import NotificationDemandeEnchaire

def global_notifications(request):
    if request.path.startswith('/admin/') and request.user.is_staff:
        return {
            'global_notifications': NotificationDemandeEnchaire.objects.filter(is_read=False)
        }
    return {}
