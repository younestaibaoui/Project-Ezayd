from django.shortcuts import render

def notifications_view(request):
    # Exemple statique ou récupérer des objets Notification
    notifications = {
        1 : 'new enchaire',
        2 : 'enchaire active',
        3 : 'objet auctioned',
    }  # Exemple : Notification.objects.filter(user=request.user)
    return render(request, 'notifications.html', {'notifications': notifications})
