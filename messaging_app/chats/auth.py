class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        user, token =super().authenticate(request)
        
        if not user.is_active:
            raise AuthenticationFailed("Your account has been Deactivated")
        
        return user, token