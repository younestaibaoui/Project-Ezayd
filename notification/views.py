from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def notifications_view(request):

    user = request.user
    notifications = user.notifications.all().order_by('-created_at')
    
    context = {
        'user': user,
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count(),
    } 

    return render(request, 'notifications.html', context)
