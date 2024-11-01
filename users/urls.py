from django.urls import path
from . import views as v

urlpatterns = [
    path("account/", v.AccountDetailView.as_view(), name="account"),
    path('edit_profile/', v.UpdateUserInfo.as_view(), name='edit_profile'),
    path("change_password/", v.UpdateUserPassword.as_view(), name="change_password"),
    path("change_email/", v.UpdateEmailView.as_view(), name="change_email"),
    path("delete_user/", v.UserDeleteView.as_view(), name="account_delete")
]# Delete user account
