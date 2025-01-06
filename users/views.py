from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth import get_user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView, View, TemplateView, FormView
from users.models import Profile
from django import forms
import os
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .forms import CustomChangePasswordForm
from allauth.account.views import PasswordChangeView, EmailView, PasswordResetFromKeyDoneView, ConfirmEmailView, \
    SignupView,PasswordResetView
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages import get_messages
from django.contrib.auth import logout
class SignupView(SignupView):
    def form_valid(self, form):
        response=super().form_valid(form)
        storage=get_messages(self.request)
        for message in storage:
            pass
        messages.success(self.request, "Registration successful! Please check your email to verify your account.")
        return redirect("account_login")
class ProfileView(LoginRequiredMixin,DetailView):
    model = Profile
    template_name = "users/profile.html"

    def get_object(self):
        self.user=get_user(self.request)
        return self.user.profile

class ProfileUpdateView(LoginRequiredMixin,UpdateView):
    model=Profile
    template_name="users/update_profile.html"
    fields=["first_name","last_name","phone_number","image"]
    success_url=reverse_lazy("users:profile_view")

    def get_object(self):
        self.user=get_user(self.request)
        return self.user.profile

    def get_form(self, *args, **kwargs):
        # Retrieve the default form
        form = super().get_form(*args, **kwargs)
        # Customize the 'image' field widget
        form.fields['image'].widget = forms.FileInput(attrs={
            'class': 'block w-full p-2 border rounded-md cursor-pointer',
            'accept': 'image/*'  # Only allow image uploads
        })
        return form

    def form_valid(self, form):
        profile = self.get_object()
        if profile.image and profile.image.name != 'avatars/default.jpg':
            profile.image.delete(save=False)  # Delete the old image
        return super().form_valid(form)

    def clean_image(self):
        image = self.cleaned_data['image']
        if image:
            extension = os.path.splitext(image.name)[1].lower()
            if extension not in settings.ALLOWED_IMAGE_FILETYPES:
                raise forms.ValidationError("Image file type is not allowed.")
            if image.size > settings.MAX_IMAGE_SIZE:
                raise forms.ValidationError("Image file size is too large.")
        return image


class ResendVerificationEmail(View):
    def get(self, request, *args, **kwargs):
        return render(request, "users/resend_email_verification.html")

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")

        # Validate email presence and format
        if not email:
            messages.error(request, "Please enter your email address.")
            return redirect("user:resend_email_verification")
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return redirect("users:resend_email_verification")

        # Check if the email exists and resend confirmation if applicable
        try:
            email_address = EmailAddress.objects.get(email=email)
            if email_address.verified:
                messages.info(request, "Your email address is already verified.")
            else:
                send_email_confirmation(request, email_address.user, email=email)
                messages.success(request, "Verification email has been resent.")
        except EmailAddress.DoesNotExist:
            # Avoid leaking whether an email exists
            messages.info(request, "If the email is associated with an account, a verification email will be resent.")

        return redirect("users:resend_email_verification")


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "account/password_change.html"
    partial_template_name = "account/password_reset_form_partial.html"
    success_url = reverse_lazy("users:profile_view")

    def dispatch(self, request, *args, **kwargs):
        if not request.htmx:
            return redirect("users:profile_view")
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        if self.request.htmx:
            return [self.partial_template_name]
        return [self.template_name]

    def form_valid(self, form):
        form.save()  # Save the form first
        if self.request.htmx:
            messages.success(self.request, "Your password has been changed successfully.")
            response = HttpResponse()
            response["HX-Redirect"] = self.get_success_url()
            return response
        messages.success(self.request, "Your password has been changed successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.htmx:
            form_html = render_to_string(self.partial_template_name, {'form': form}, request=self.request)
            return HttpResponse(form_html)
        return super().form_invalid(form)


class CustomEmailView(EmailView):
    template_name = "account/email.html"
    success_url = reverse_lazy("users:profile_view")
    """
    After tests put it back
    def dispatch(self, request, *args, **kwargs):
        if not request.htmx:
            return redirect("users:profile_view")
        return super().dispatch(request, *args, **kwargs)
    """
    def test_func(self):
        return not SocialAccount.objects.filter(user=self.request.user).exists()

    def handle_no_permission(self):
        messages.error(self.request, "Social account users cannot access this page.")
        return redirect("users:profile_view")

    def form_valid(self, form):
        form.save()
        if self.request.htmx:
            messages.success(self.request, "Your email address has been updated successfully.")
            response = HttpResponse()
            response["HX-Redirect"] = self.get_success_url()
            return response
        return super().form_valid(form)
class TestView(UserPassesTestMixin,TemplateView):
    template_name="users/test.html"

    def test_func(self):
        return not SocialAccount.objects.filter(user=self.request.user).exists()

    def handle_no_permission(self):
        messages.error(self.request, "Social account users cannot access this page.")
        return redirect("users:profile_view")
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context["form"]=CustomChangePasswordForm(self.request.user)
        return context

class CustomPasswordResetFromKeyDoneView(PasswordResetFromKeyDoneView):
    def get(self,request,*args,**kwargs):
        if request.user.is_authenticated:
            logout(request)
        storage=get_messages(self.request)
        for message in storage:
            pass
        messages.success(request, "Password has been reset successfully. Please login with your new password.")
        return redirect("account_login")

class ConfirmEmailView(ConfirmEmailView):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.confirm(self.request)
        storage=get_messages(self.request)
        for message in storage:
            pass
        messages.success(request, "Email has been confirmed successfully.")
        return redirect("account_login")


class CustomPasswordResetView(PasswordResetView):
    template_name = "account/password_reset.html"
    success_url = reverse_lazy('account_login')

    def dispatch(self, request, *args, **kwargs):
        # Remove any login requirement
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in.")
            return redirect(reverse_lazy('users:profile_view'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Password reset instructions have been sent to {email}."
        )
        return response
