from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import User, Conversation, Message
from .serializers import (
    ConversationSerializer,
    ConversationListSerializer,
    MessageSerializer,
    MessageCreateSerializer,
    UserSerializer
)

"PUT", "PATCH", "DELETE"
"conversation_id", "HTTP_403_FORBIDDEN"


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for Conversation model."""
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['participants__first_name', 'participants__last_name', 'participants__email']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return conversations where the current user is a participant."""
        return Conversation.objects.filter(participants=self.request.user).prefetch_related(
            'participants', 'messages', 'messages__sender'
        )
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer
    
    def perform_create(self, serializer):
        """Ensure current user is included in participants."""
        participants = serializer.validated_data.get('participants', [])
        if self.request.user not in participants:
            participants.append(self.request.user)
        serializer.save(participants=participants)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Add a participant to an existing conversation."""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {"error": "user_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if user not in conversation.participants.all():
            conversation.participants.add(user)
            return Response(
                {"message": "Participant added successfully."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "User is already a participant."},
                status=status.HTTP_200_OK
            )
    
    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        """Remove a participant from a conversation."""
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {"error": "user_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if user in conversation.participants.all():
            conversation.participants.remove(user)
            return Response(
                {"message": "Participant removed successfully."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "User is not a participant in this conversation."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages for a specific conversation."""
        conversation = self.get_object()
        messages = conversation.messages.all().select_related('sender')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for Message model."""
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['message_body', 'sender__first_name', 'sender__last_name']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']
    
    def get_queryset(self):
        """Return messages where the current user is a participant in the conversation."""
        return Message.objects.filter(
            conversation__participants=self.request.user
        ).select_related('sender', 'conversation')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return MessageCreateSerializer
        return MessageSerializer
    
    def perform_create(self, serializer):
        """Set the sender to the current user and mark as unread."""
        message = serializer.save(sender=self.request.user, is_read=False)
        
        # Mark message as read for the sender immediately
        message.is_read = True
        message.save()
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark a message as read."""
        message = self.get_object()
        
        # Only mark as read if the current user is not the sender
        if message.sender != request.user:
            message.is_read = True
            message.save()
            return Response(
                {"message": "Message marked as read."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Cannot mark your own message as read."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get all unread messages for the current user."""
        unread_messages = Message.objects.filter(
            conversation__participants=request.user,
            is_read=False
        ).exclude(sender=request.user).select_related('sender', 'conversation')
        
        serializer = MessageSerializer(unread_messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sent(self, request):
        """Get all messages sent by the current user."""
        sent_messages = Message.objects.filter(
            sender=request.user
        ).select_related('conversation')
        
        serializer = MessageSerializer(sent_messages, many=True)
        return Response(serializer.data)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for User model (read-only)."""
    
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name', 'last_name', 'email']
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user information."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search users by email, first name, or last name."""
        query = request.query_params.get('q', '')
        
        if not query:
            return Response(
                {"error": "Query parameter 'q' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        users = User.objects.filter(
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(user_id=request.user.user_id)
        
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

from rest_framework import viewsets, permissions
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        # Limit conversations to only those the user participates in
        return Conversation.objects.filter(participants=self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        # Limit messages to only conversations the user participates in
        return Message.objects.filter(conversation__participants=self.request.user)


