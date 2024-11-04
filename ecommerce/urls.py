from users import views as user_v
import users, products
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from debug_toolbar import urls as debug_toolbar_urls

urlpatterns = [
    path("",user_v.index,name="index"),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path("index/",user_v.index,name="index"),
    path("user/",include("users.urls")),
    path("__debug__/",include(debug_toolbar_urls)),
    path("products/",include("products.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)