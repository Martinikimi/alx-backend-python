from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework import permissions

class IsOwner(BasePermission):
    """
    Custom permission to allow users to only access their own objects.
    """

    def has_object_permission(self, request, view, obj):
        # Assuming messages have a `sender` field or conversations have `user`
        return obj.user == request.user or obj.sender == request.user


class IsParticipantOfConversation(BasePermission):
    """
    Custom permission:
    - Only authenticated users can access.
    - Only participants of a conversation can send, view, update, or delete messages.
    """

    def has_permission(self, request, view):
        # User must be authenticated to access any endpoint
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check if the user is part of the conversation.
        Assumes:
        - Conversation model has participants (ManyToMany to User).
        - Message model has conversation field linking to Conversation.
        """
        if hasattr(obj, "participants"):  # If object is a conversation
            return request.user in obj.participants.all()
        elif hasattr(obj, "conversation"):  # If object is a message
            return request.user in obj.conversation.participants.all()
        return False

from rest_framework.permissions import BasePermission


class IsParticipantOfConversation(BasePermission):
    """
    Custom permission:
    - Only authenticated users can access.
    - Only participants in a conversation can send, view, update, or delete messages.
    """

    def has_permission(self, request, view):
        # Must be authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Object-level permissions:
        - Allow GET, POST, PUT, PATCH, DELETE only if the user
          is a participant in the related conversation.
        """
        # If obj is a Conversation
        if hasattr(obj, "participants"):
            return request.user in obj.participants.all()

        # If obj is a Message (assumes message has a conversation foreign key)
        if hasattr(obj, "conversation"):
            return request.user in obj.conversation.participants.all()

        return False


