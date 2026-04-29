from .models import Notification

def notification_context(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        latest_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
        return {
            'unread_notifications_count': unread_count,
            'latest_notifications': latest_notifications
        }
    return {}
