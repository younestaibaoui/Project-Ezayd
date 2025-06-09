from django.core.mail import send_mail
from django.conf import settings
from .models import EmailVerificationToken
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserRegistrationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def inscription_view(request):

    # Si l'utilisateur est déjà connecté, on le redirige vers l'accueil
    if request.user.is_authenticated:
        return redirect('accueil')

    if request.method == "POST":
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            # Créer un token de vérification
            token = EmailVerificationToken.objects.create(user=user)

            verification_url = request.build_absolute_uri(
                reverse('email_verification', args=[str(token.token)])
            )

            send_mail(
                'Confirmez votre adresse email',
                f'Bonjour {user.username},\n\nMerci de confirmer votre adresse email en cliquant sur ce lien :\n{verification_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            messages.success(
                request,
                "Votre compte a été créé avec succès. Un email de confirmation vous a été envoyé."
            )
            return redirect('connexion')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = UserRegistrationForm()
    return render(request, 'inscription.html', {'form': form})


def connexion_view(request):
    # Si l'utilisateur est déjà connecté, on le redirige vers l'accueil
    if request.user.is_authenticated:
        return redirect('accueil')

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            if getattr(user, 'email_verified', False):
                login(request, user)
                messages.success(request, f"Bienvenue {user.username} !")
                return redirect('accueil')
            else:
                messages.warning(request, "Veuillez vérifier votre adresse email avant de vous connecter.")
        else:
            messages.error(request, "Email ou mot de passe invalide.")
    return render(request, "connexion.html")

def deconnexion_view(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('connexion')

def email_verification_view(request, token):
    token_obj = get_object_or_404(EmailVerificationToken, token=token)

    # Vérifier si le token a expiré
    expiration_time = token_obj.created_at + timezone.timedelta(hours=24)
    if timezone.now() > expiration_time:
        messages.error(request, "Ce lien de confirmation a expiré. Veuillez vous réinscrire.")
        return redirect('inscription')

    # Valider l’email
    user = token_obj.user
    user.email_verified = True
    user.save()

    token_obj.delete()
    messages.success(request, "Votre email a bien été confirmé. Vous pouvez maintenant vous connecter.")
    return redirect('connexion')
