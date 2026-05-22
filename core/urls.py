"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
import os


from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from drf_yasg.generators import OpenAPISchemaGenerator
from .views import FileUploadView, FileServeView
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
current_schemes=["https", "http"]
current_env =os.getenv("ENVIRONMENT")   
    

if current_env == 'LOCAL':        
    current_schemes=["http", "https"]

class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):



    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = current_schemes
        return schema

schema_view = get_schema_view(
    openapi.Info(
        title="SIPROB API",
        default_version='v1',
        description="Rutas de SIPROB API",
    ),
    generator_class=BothHttpAndHttpsSchemaGenerator, # Here
    public=True,
    permission_classes=(permissions.AllowAny,),
)

def welcome_text(request):
    return HttpResponse("SIPROB API V1")

def current_datetime(request):
    return JsonResponse({"status": "success", "data": {"date_time": timezone.now().isoformat()}})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', welcome_text),
    path('date_time/', current_datetime, name='current-datetime'),
    path('detainees/', include('detainees.urls')),
    path('', include('records.urls')),
    path('districts/', include('districts.urls')),
    path('', include('users.urls')),
    path('', include('roles.urls')),
    path('', include('shifts.urls')),   
    path('', include('reports.urls')),   
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'), 
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('serve/<str:filename>/', FileServeView.as_view(), name='file-serve')
    # path('serve/<str:filename>/', serve_file, name='serve-file')   
    #re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
