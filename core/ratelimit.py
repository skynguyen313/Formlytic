from django.http import JsonResponse
from functools import wraps
from django_ratelimit.decorators import ratelimit

def custom_key(group, request_or_view):
    if hasattr(request_or_view, 'META'):
        req = request_or_view
    elif hasattr(request_or_view, 'request'):
        req = request_or_view.request
    else:
        req = request_or_view

    token = req.headers.get('Authorization')
    if not token:
        ip = req.META.get('HTTP_X_FORWARDED_FOR')
        if ip:
            ip = ip.split(',')[0].strip()
        else:
            ip = req.META.get('REMOTE_ADDR', 'unknown')
        token = ip

    key = f'{token}:{req.path}'
    return key



def rate_limit_decorator(rate='5/m'):
    def decorator(func):
        @wraps(func)
        @ratelimit(key=custom_key, rate=rate, block=False)  # block=False allows processing to continue despite the limit
        def wrapper(request, *args, **kwargs):
            # If the request is limited (not enough time to send another request)
            if getattr(request, 'limited', False):
                return JsonResponse(
                    {'error': 'You have sent too many requests. Please try again later.'},
                    status=429
                )
            return func(request, *args, **kwargs)
        return wrapper
    return decorator