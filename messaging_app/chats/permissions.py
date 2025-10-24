from rest_framework import permissions

class IsMessageOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Users can only access their own messages
        return obj.user == request.user
    
