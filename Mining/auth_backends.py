from django.contrib.auth.backends import ModelBackend
from datetime import timedelta

class CustomSessionBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username, password, **kwargs)
        if user and user.is_authenticated:
            # Extend the session to 1 year
            request.session.set_expiry(timedelta(days=365))
        return user
