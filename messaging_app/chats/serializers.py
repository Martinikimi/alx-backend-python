from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=False,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'user_id', 
            'first_name', 
            'last_name', 
            'email', 
            'phone_number', 
            'role', 
            'password',
            'confirm_password',
            'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }
    
    def validate_email(self, value):
        """Validate email format and uniqueness."""
        if User.objects.filter(email=value).exists():
            raise ValidationError("A user with this email already exists.")
        return value
    
    def validate(self, data):
        """Validate password confirmation."""
        if 'password' in data and 'confirm_password' in data:
            if data['password'] != data['confirm_password']:
                raise ValidationError({"confirm_password": "Passwords do not match."})
        return data
    
    def create(self, validated_data):
        """Create a new user with encrypted password."""
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        """Update a user, handling password separately."""
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model."""
    
    sender = UserSerializer(read_only=True)
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='sender', 
        write_only=True
    )
    message_body = serializers.CharField(
        required=True,
        max_length=1000,
        error_messages={
            'blank': 'Message body cannot be blank.',
            'max_length': 'Message cannot exceed 1000 characters.'
        }
    )
    
    class Meta:
        model = Message
        fields = [
            'message_id', 
            'sender', 
            'sender_id', 
            'conversation', 
            'message_body', 
            'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at']
    
    def validate_message_body(self, value):
        """Validate message body is not empty after stripping."""
        if not value.strip():
            raise ValidationError("Message body cannot be empty.")
        return value.strip()


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model with nested messages."""
    
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        many=True, 
        source='participants', 
        write_only=True
    )
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 
            'participants', 
            'participant_ids', 
            'messages', 
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']
    
    def validate_participant_ids(self, value):
        """Validate that there are at least 2 participants."""
        if len(value) < 2:
            raise ValidationError("A conversation must have at least 2 participants.")
        return value
    
    def create(self, validated_data):
        """Create a conversation with participants."""
        participants = validated_data.pop('participants', [])
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.set(participants)
        return conversation
    
    def update(self, instance, validated_data):
        """Update a conversation, including participants."""
        participants = validated_data.pop('participants', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if participants is not None:
            instance.participants.set(participants)
        
        instance.save()
        return instance


class ConversationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing conversations."""
    
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    last_message_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 
            'participants', 
            'last_message', 
            'last_message_preview',
            'unread_count', 
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']
    
    def get_last_message(self, obj):
        """Get the last message in the conversation."""
        last_message = obj.messages.order_by('-sent_at').first()
        if last_message:
            return {
                'message_body': last_message.message_body,
                'sent_at': last_message.sent_at,
                'sender_id': last_message.sender.user_id
            }
        return None
    
    def get_last_message_preview(self, obj):
        """Get a preview of the last message."""
        last_message = obj.messages.order_by('-sent_at').first()
        if last_message:
            preview = last_message.message_body[:50]
            if len(last_message.message_body) > 50:
                preview += '...'
            return preview
        return None
    
    def get_unread_count(self, obj):
        """Get count of unread messages for the current user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0


class UserWithConversationsSerializer(UserSerializer):
    """User serializer with nested conversations."""
    
    conversations = ConversationListSerializer(many=True, read_only=True)
    
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['conversations']


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer specifically for creating messages."""
    
    message_body = serializers.CharField(
        required=True,
        max_length=1000,
        error_messages={
            'blank': 'Message body cannot be blank.',
            'max_length': 'Message cannot exceed 1000 characters.'
        }
    )
    
    class Meta:
        model = Message
        fields = ['conversation', 'message_body']
    
    def validate_message_body(self, value):
        """Validate message body is not empty after stripping."""
        if not value.strip():
            raise ValidationError("Message body cannot be empty.")
        return value.strip()
