from django.db import models

class NotificationEnchaire(models.Model):
    enchaire = models.ForeignKey(
        'Ezayd.Enchaire',  # app_label.ModelName as a string
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    user = models.ForeignKey(
        'perso.UserAccount',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user} about Enchaire #{self.enchaire.id}"

