from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def accueil(request):
    
    return render(request, 'accueil.html', {'user': request.user})


