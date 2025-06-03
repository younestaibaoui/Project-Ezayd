from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import uuid


class UserAccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_kwargs):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        username = email.split('@')[0]
        user = self.model(email=email, username=username, **extra_kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_kwargs):
        user = self.create_user(
            email,
            password=password,
            **extra_kwargs
        )
        user.is_admin = True
        user.is_superuser = True  # Géré par PermissionsMixin
        user.save(using=self._db)
        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="Email", max_length=255, unique=True)
    username = models.CharField(max_length=25, blank=True, null=True)
    first_name = models.CharField(max_length=25, blank=True, null=True)
    last_name = models.CharField(max_length=25, blank=True, null=True)
    is_active = models.BooleanField(default=True)       # Pour désactiver un compte
    is_admin = models.BooleanField(default=False)       # Pour les privilèges d'admin
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    special_profile = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    last_chance_participation_used = models.BooleanField(default=False)
    bio = models.TextField(default=None, null=True, blank=True)
    pfp = models.ImageField(null=True, blank=True, upload_to='images/')  # Nécessite Pillow

    objects = UserAccountManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username or self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin or super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        return self.is_admin or super().has_module_perms(app_label)

    @property
    def is_staff(self):
        # Django utilise cette propriété pour déterminer si l’utilisateur peut accéder à l’admin
        return self.is_admin


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
