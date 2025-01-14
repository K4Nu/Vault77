from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth import get_user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView, View, TemplateView, FormView, DeleteView
from users.models import Profile, CustomUser
from django import forms
import os
from django.contrib import messages
from .forms import CustomChangePasswordForm,CustomChangeEmailForm,ProfileUpdateForm,ResendEmailForm
from allauth.account.views import PasswordChangeView, EmailView, PasswordResetFromKeyDoneView, ConfirmEmailView, \
    SignupView,PasswordResetView
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages import get_messages
from django.contrib.auth import logout
from allauth.account.utils import get_adapter
from django.db import transaction
from django.forms import modelform_factory


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


class ProfileUpdateView(LoginRequiredMixin, FormView):
    template_name = "users/update_profile.html"
    form_class = ProfileUpdateForm
    success_url = reverse_lazy("users:profile_view")

    def get_initial(self):
        profile = self.request.user.profile
        return {
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'phone_number': profile.phone_number,
        }

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields['image'].widget = forms.FileInput(attrs={
            'class': 'block w-full p-2 border rounded-md cursor-pointer',
            'accept': 'image/*'
        })
        form.fields['image'].required = False
        return form

    def form_valid(self, form):
        profile = self.request.user.profile
        profile.first_name = form.cleaned_data['first_name']
        profile.last_name = form.cleaned_data['last_name']
        profile.phone_number = form.cleaned_data['phone_number']

        if form.cleaned_data.get('image'):
            if profile.image and not profile.image.name.startswith('avatars/default'):
                profile.image.delete(save=False)
            profile.image = form.cleaned_data['image']

        profile.save()
        messages.success(self.request, "Profile updated successfully")
        return super().form_valid(form)
class ResendVerificationEmail(FormView):
    template_name = "users/resend_email_verification.html"
    form_class = ResendEmailForm  # Use form_class instead of form

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        email = get_adapter().clean_email(email)
        query = EmailAddress.objects.filter(email=email).first()

        if query and not query.verified:
            send_email_confirmation(self.request, query.user,
                                    email=email)  # Use query.user instead of self.users.first()
            return redirect("users:update_profile")

        messages.error(self.request, "Email not found or already verified.")
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
        storage=get_messages(self.request)
        for message in storage:
            pass
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


class CustomEmailView(FormView):
    template_name = "users/email.html"
    form_class = CustomChangeEmailForm
    success_url = reverse_lazy("users:profile_view")

    def dispatch(self, request, *args, **kwargs):
        if SocialAccount.objects.filter(user=self.request.user).exists():
            messages.error(request, "You cannot change your email using a social account.")
            return redirect("users:profile_view")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data['email1']  # Already cleaned by form
        user = self.request.user

        # Email uniqueness is already checked in form's clean method
        if user.email != email:
            with transaction.atomic():
                # Update existing email addresses
                EmailAddress.objects.filter(user=user).delete()
                EmailAddress.objects.create(user=user, email=email, primary=True, verified=False)

                # Update user email
                user.email = email
                user.save()

                # Send confirmation email
                send_email_confirmation(self.request, user, email=email)
                messages.success(self.request, "Email has been changed successfully.")
                logout(self.request)

        return super().form_valid(form)

class UserDashboardView(UserPassesTestMixin, TemplateView):
    template_name = "users/user_dashboard.html"

    def test_func(self):
        return not SocialAccount.objects.filter(user=self.request.user).exists()

    def handle_no_permission(self):
        messages.error(self.request, "Social account users cannot access this page.")
        return redirect("users:profile_view")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add password form (using allauth's form)
        context["password_form"] = CustomChangePasswordForm(user=self.request.user)

        # Add email form
        context["email_form"] = CustomChangeEmailForm()

        # Add profile form
        ProfileForm = modelform_factory(
            Profile,
            fields=["first_name", "last_name", "phone_number", "image"]
        )
        context["profile_form"] = ProfileForm(
            instance=self.request.user.profile
        )

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


class ConfirmEmailView(ConfirmEmailView,):
    def get(self, request, *args, **kwargs):
        try:
            # Get and confirm the email confirmation object
            self.object = self.get_object()
            self.object.confirm(self.request)

            # Clear any existing messages
            storage = get_messages(self.request)
            for message in storage:
                pass  # Clear existing messages

            # Add success message
            messages.success(request, "Email has been confirmed successfully.")

            return redirect("account_login")

        except Exception as e:
            messages.error(request, "Invalid or expired confirmation link.")
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

class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = "users/delete_user.html"
    success_url = reverse_lazy("account_logout")

    def get_object(self, queryset=None):
        # Ensure users can only delete their own account
        return self.request.user

    def delete(self, request, *args, **kwargs):
        EmailAddress.objects.filter(user=self.request.user).delete()
        SocialAccount.objects.filter(user=self.request.user).delete()  # Deletes all social accounts
        messages.success(self.request, "User deleted successfully")
        return super().delete(request, *args, **kwargs)