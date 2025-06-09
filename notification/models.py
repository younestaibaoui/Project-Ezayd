from django.db import models

class NotificationEnchaire(models.Model):
    enchaire = models.ForeignKey(
        'Ezayd.Enchaire', 
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,            
        blank=True,             
        default=None,
    )
    enchaireObjet = models.ForeignKey(
        'Ezayd.EnchaireObjet', 
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,            
        blank=True,             
        default=None,
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
        if self.enchaire:
            return f"Notification for {self.user} about Enchaire #{self.enchaire.id if self.enchaire else 'Unknown'}"
        else: 
            return f"Notification for {self.user} about EnchaireObjet #{self.enchaireObjet.id if self.enchaireObjet else 'Unknown'}"

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