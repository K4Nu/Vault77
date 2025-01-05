from django.urls import path
from . import views

app_name = "users"

urlpatterns=[
        path("",views.ProfileView.as_view(),name="profile_view"),
        path("update/",views.ProfileUpdateView.as_view(),name="profile_update"),
        path("resend-email-verification/", views.ResendVerificationEmail.as_view(), name="resend_email_verification"),
        path("test-modal/",views.TestView     .as_view(),name="test"),
]