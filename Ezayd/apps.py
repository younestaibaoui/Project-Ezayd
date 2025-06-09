#to load signals
from django.apps import AppConfig

class EzaydConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Ezayd'

    def ready(self):
        import Ezayd.signals
