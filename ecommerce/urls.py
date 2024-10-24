from django.contrib import admin
from django.urls import path, include
from users import views as user_v

urlpatterns = [
    path("",user_v.index),
    path('admin/', admin.site.urls),
    path("account/",user_v.AccountDetailView.as_view(),name="account"),
    path('accounts/', include('allauth.urls')),
    path('edit_profile/', user_v.UpdateUserInfo.as_view(), name='edit_profile'),
    path("change_password/",user_v.UpdateUserPassword.as_view(),name="change_password"),
    path("index/",user_v.index,name="index"),
    path("users/",user_v.UserListView.as_view(),name="show-users"),
]
