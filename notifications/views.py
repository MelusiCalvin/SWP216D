from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification

@login_required
def notifications(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-created_at')
    
    # Mark all as read
    if request.method == 'POST':
        notifications.update(is_read=True)
        return redirect('notifications')
    
    return render(request, 'notifications/notifications.html', {
        'notifications': notifications,
    })

@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    return JsonResponse({'status': 'success'})

@login_required
def notification_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})

print("Notification views created")