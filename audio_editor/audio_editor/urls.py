from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from oauth2_provider.views import AuthorizationView


schema_view = get_schema_view(
   openapi.Info(
      title='Audio Editor API',
      default_version='v1',
      description='in development...',
      terms_of_service='',
      contact=openapi.Contact(email=''),
      license=openapi.License(name=''),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),      # !_!
)

api_version = f'{settings.API_VERSION}/'

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    # oauth2 authorization - must be in root
    path('authorize/', AuthorizationView.as_view(), name="authorize"),
    # API
    path('api/', include([
        path('documentation/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path(api_version, include([
            # caution! non-namespaced same-prefix urls must be unique
            path('', include('users.urls_api')),
            path('', include('app_main.urls_api')),
        ])),
    ])),
    # app components
    path('accounts/', include('users.urls')),
    path('', include('app_main.urls')),
]

# local media
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
