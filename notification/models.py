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

class NotificationDemandeEnchaire(models.Model):
    user = models.ForeignKey(
        'perso.UserAccount',
        on_delete=models.CASCADE,
        related_name='notifications_demande'  # change this to a more descriptive name
    )
    enchaire = models.ForeignKey(
        'Ezayd.Enchaire',
        on_delete=models.CASCADE,
        default=2,
        related_name='notifications_demande'  # change as needed
    )
    message = models.CharField(max_length=255)
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)