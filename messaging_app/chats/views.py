from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Message
from .serializers import MessageSerializer
from .permissions import IsMessageOwner
from .pagination import MessagePagination
from .filters import MessageFilter
from django_filters.rest_framework import DjangoFilterBackend

class MessageListCreate(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsMessageOwner]
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend] 
    filterset_class = MessageFilter
    
    def get_queryset(self):
        # Users can only see their own messages
        return Message.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Automatically assign the current user to new messages
        serializer.save(user=self.request.user)
