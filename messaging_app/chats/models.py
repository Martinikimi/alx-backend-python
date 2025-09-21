
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """Custom User model extending Django's AbstractUser."""
    
    class Role(models.TextChoices):
        GUEST = 'guest', 'Guest'
        HOST = 'host', 'Host'
        ADMIN = 'admin', 'Admin'
    
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    first_name = models.CharField(max_length=150, null=False)
    last_name = models.CharField(max_length=150, null=False)
    email = models.EmailField(unique=True, null=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Password field is inherited from AbstractUser as 'password'
    # The AbstractUser already has a password field that stores hashed passwords
    
    # Override username field to use email instead
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'user'
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_email')
        ]
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def set_password(self, raw_password):
        """Override set_password to ensure password is hashed properly."""
        super().set_password(raw_password)
    
    def check_password(self, raw_password):
        """Check if the provided password matches the hashed password."""
        return super().check_password(raw_password)


class Conversation(models.Model):
    """Conversation model to track which users are involved in a conversation."""
    
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'conversation'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        participant_names = ", ".join([f"{user.first_name} {user.last_name}" for user in self.participants.all()[:3]])
        return f"Conversation {self.conversation_id} - Participants: {participant_names}"


class Message(models.Model):
    """Message model containing sender and conversation information."""
    
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message_body = models.TextField(null=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message'
        ordering = ['-sent_at']
        constraints = [
            models.UniqueConstraint(fields=['message_id'], name='unique_message_id')
        ]
        indexes = [
            models.Index(fields=['sender']),
            models.Index(fields=['conversation']),
            models.Index(fields=['sent_at']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender.email} at {self.sent_at}"
