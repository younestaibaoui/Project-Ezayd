from django.contrib import admin
from django.urls import path
from django.urls import include
from .views import *

urlpatterns = [
    path('test',test,name='test'),  # accessible via /test
    path('test2',test2,name='test2'),  # accessible via /test2
]
