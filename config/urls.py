from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions


# schema_view = get_schema_view(
#     openapi.Info(
#         title='Hackathon3 API',
#         default_version='v1',
#         description='Education Platform',
#         terms_of_service="https://www.google.com/policies/terms/",
#         contact=openapi.Contact(email="contact@snippets.local"),
#         license=openapi.License(name="BSD License"),
#     ),
#     public=True,
#     permission_classes=[permissions.AllowAny]
# )
schema_view = get_schema_view(
    openapi.Info(
        title="Hackathon3 API",
        default_version='v1',
        description="Ed platform",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="contact@yourapp.com"),
        license=openapi.License(name="Your License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/account/', include('account.urls')),
    path('api/', include('course.urls')),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema_swagger-ui'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
