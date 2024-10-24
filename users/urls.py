from django.contrib import admin
from django.urls import path, include
from . import views as v

urlpatterns = [
    path('admin/', admin.site.urls),
    path("account/",v.AccountDetailView.as_view(),name="account"),
    path('edit_profile/', v.UpdateUserInfo.as_view(), name='edit_profile'),
    path("change_password/",v.UpdateUserPassword.as_view(),name="change_password"),
    path("users/",v.UserListView.as_view(),name="show-users"),
    path("change_email/",v.UpdateEmailView.as_view(),name="change_email"),
]
