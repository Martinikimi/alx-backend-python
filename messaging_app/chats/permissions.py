from rest_framework.permissions import BasePermission
from rest_framework import permissions

class IsOwner(BasePermission):
    """
    Custom permission to allow users to only access their own objects.
    """

    def has_object_permission(self, request, view, obj):
        # Assuming messages have a `sender` field or conversations have `user`
        return obj.user == request.user or obj.sender == request.user
