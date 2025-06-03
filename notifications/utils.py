from .models import Notification

def send_notification(user, notification_type, title, message, ride=None):
    """
    Utility function to send a notification to a user.
    
    Args:
        user: The user to send the notification to
        notification_type: The type of notification
        title: The notification title
        message: The notification message
        ride: Optional ride object related to the notification
    """
    Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        ride=ride
    )
    
    # In a real app, this would also send push notifications, emails, etc.
    # based on user preferences

print("Notification utilities created")