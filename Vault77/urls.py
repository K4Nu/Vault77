from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path("user/", include("users.urls"),name="users"),
    path("__reload__/", include("django_browser_reload.urls")),
    path('accounts/', include('allauth.urls')),
]
if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)