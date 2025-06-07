from django.urls import path
from .views import *

urlpatterns = [
    path('', notifications_view , name='notifications'),
    path('mark-as-read/<int:notification_id>/', mark_as_read , name='mark_as_read'),
    path('mark-all-as-read/', mark_all_as_read , name='mark_all_as_read'),
]

