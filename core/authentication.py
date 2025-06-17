from rest_framework_simplejwt.authentication import JWTAuthentication
import threading

_thread_locals = threading.local()

def get_current_user():
    return getattr(_thread_locals, 'user', None)

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        auth_result = super().authenticate(request)
        if auth_result is not None:
            user, token = auth_result
            _thread_locals.user = user
        return auth_result
