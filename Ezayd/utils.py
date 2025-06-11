# Ezayd/utils.py
from .models import Enchaire
import threading

def update_encheres_en_arriere_plan():
    for ench in Enchaire.objects.all():
        ancien_etat = ench.etat
        ench.save()  # déclenche la mise à jour d’état


def lancer_mise_a_jour_enchere_thread():
    thread = threading.Thread(target=update_encheres_en_arriere_plan)
    thread.daemon = True  # meurt avec le process Django
    thread.start()