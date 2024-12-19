from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
from django.conf import settings
from django.contrib.auth import get_user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render,redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, FormView, UpdateView,View
from users.models import Profile
from django import forms
from uuid import uuid4
import os
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

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