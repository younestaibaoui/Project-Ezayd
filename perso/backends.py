from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailVerifiedBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # On suppose que le username est l'email
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        
        if user.check_password(password) and user.email_verified:
            return user
        return None
