from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/auth/', include('social_accounts.urls')),
    path('api/organizers/', include('organizers.urls')),
    path('api/notify/', include('notify_app.urls')),
    path('api/psychology/', include('psychology_app.urls')), 
    path('api/chatbot/', include('chatbot_app.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)