from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = [
            'user_id', 
            'first_name', 
            'last_name', 
            'email', 
            'phone_number', 
            'role', 
            'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True}  # Password is write-only
        }
    
    def create(self, validated_data):
        """Create a new user with encrypted password."""
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        """Update a user, handling password separately."""
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
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 
            'participants', 
            'last_message', 
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
