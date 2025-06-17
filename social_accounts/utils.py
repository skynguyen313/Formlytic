from django.contrib.auth import authenticate
from firebase_admin import auth
from rest_framework.exceptions import AuthenticationFailed


class Google:
    @staticmethod
    def validate(id_token):
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except auth.ExpiredIdTokenError:
            raise AuthenticationFailed('Token has expired.')
        except auth.InvalidIdTokenError:
            raise AuthenticationFailed('Invalid token.')
        except Exception as e:
            raise AuthenticationFailed(f'Authentication failed: {str(e)}')