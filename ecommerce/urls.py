from users import views as user_v
import users
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("",user_v.index),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path("index/",user_v.index,name="index"),
    path("user/",include("users.urls"))
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)