"""
URL configuration for DjangoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from users.views import CustomPasswordChangeView, CustomEmailView, CustomPasswordResetFromKeyDoneView, ConfirmEmailView, \
    SignupView,CustomPasswordResetView,ResendVerificationEmail
import debug_toolbar
urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('users.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
    path('accounts/email/', CustomEmailView.as_view(), name='account_email'),
    path("accounts/signup/",SignupView.as_view(),name="account_signup"),
    path("accounts/resend-email-verification/", ResendVerificationEmail.as_view(), name="resend_email_verification"),
    path("accounts/password/reset/",CustomPasswordResetView.as_view(),name="account_reset_password"),
    path("accounts/confirm-email/<str:key>/", ConfirmEmailView.as_view(), name="account_confirm_email"),
    #path("accounts/password/reset/key/<str:uidb64>/<str:key>/",CustomPasswordResetFromKeyDoneView.as_view(),name="account_reset_password_from_key"),
    path("accounts/password/reset/key/done/",CustomPasswordResetFromKeyDoneView.as_view(),name="account_reset_password_from_key_done"),
    #path("accounts/confirm-email/",ConfirmEmailView.as_view(),name="account_confirm_email"),
    path('accounts/password/change/', CustomPasswordChangeView.as_view(), name='account_change_password'),
    path('accounts/', include('allauth.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
]
if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)