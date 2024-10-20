from django.contrib import admin
from django.urls import path, include
from users import views as user_v

urlpatterns = [
    path('admin/', admin.site.urls),
    path("account/",user_v.AccountDetailView.as_view(),name="account"),
    path('accounts/', include('allauth.urls')),
    path("index/",user_v.index,name="index")
]
