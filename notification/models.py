from django.db import models
from Ezayd.models import Enchaire
from perso.models import(
    UserAccount,
    UserAccoundManage,
)

class NotificationEnchaire(models.Model):
    user = models.ForeignKey(
        "perso.UserAccount",
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    enchaire = models.ForeignKey(
        "Enchaire",
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user} about Enchaire #{self.enchaire.id}"

