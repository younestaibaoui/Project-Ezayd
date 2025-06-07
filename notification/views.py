from django.shortcuts import render, redirect
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


@login_required
def mark_as_read(request, notification_id):
    user = request.user
    try:
        notification = user.notifications.get(id=notification_id)
        notification.is_read = True
        notification.save()
    except user.notifications.model.DoesNotExist:
        pass

    return redirect('details_enchaire',notification.enchaire.id)


# mark all notifications as read
@login_required
def mark_all_as_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('notifications')  # Remplace par ton nom d'URL