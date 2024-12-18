from django.conf import settings
from django.contrib.auth import get_user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, FormView, UpdateView
from users.models import Profile
from django import forms
from uuid import uuid4
import os

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
