from django.urls import path
from . import views

urlpatterns = [
    path('messages/', views.MessageListCreate.as_view(), name='message-list'),
]