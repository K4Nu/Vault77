from django.urls import path
from . import views

app_name = "users"

urlpatterns=[
        path("",views.ProfileView.as_view(),name="profile_view"),
        path("update/",views.ProfileUpdateView.as_view(),name="update_profile"),
        #path("resend-email-verification/", views.ResendVerificationEmail.as_view(), name="resend_email_verification"),
        path("user-dashboard/",views.UserDashboardView.as_view(),name="user-dashboard/"),
        path("delete-account/",views.DeleteUserView.as_view(),name="delete_account"),
]