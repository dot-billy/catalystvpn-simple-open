from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.permissions import AllowAny
from api.views import web

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Web UI
    path('', web.login_view, name='login'),
    path('dashboard/', web.dashboard_view, name='dashboard'),
    path('logout/', web.logout_view, name='logout'),
    
    # API
    path('api/', include('api.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(
        permission_classes=[AllowAny],
        authentication_classes=[]
    ), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(
        url_name='schema',
        permission_classes=[AllowAny],
        authentication_classes=[]
    ), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(
        url_name='schema',
        permission_classes=[AllowAny],
        authentication_classes=[]
    ), name='redoc'),
] 