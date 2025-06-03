from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def accueil(request):
    return render(request, 'accueil.html', {'user': request.user})

def test(request):
    return render(request, 'index.html', {})

def test2(request):
    return render(request,'inscription.html', {})