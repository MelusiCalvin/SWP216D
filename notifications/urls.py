from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications, name='notifications'),
    path('<int:notification_id>/mark-as-read/', views.mark_as_read, name='mark_notification_as_read'),
    path('count/', views.notification_count, name='notification_count'),
]