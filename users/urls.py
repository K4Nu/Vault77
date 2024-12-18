from django.urls import path
from . import views

app_name = "users"

urlpatterns=[
        path("",views.ProfileView.as_view(),name="profile_view"),
        path("update/",views.ProfileUpdateView.as_view(),name="profile_update"),
]