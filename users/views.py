from django.shortcuts import render
from django.urls import reverse_lazy,reverse
from django.http import HttpResponse
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView, FormView,ListView
from .models import AppUser
from .forms import PasswordChangeForm,EmailChangeForm, UserInfoForm
from django.contrib.auth import update_session_auth_hash


def index(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)


class AccountDetailView(LoginRequiredMixin,DetailView):
    template_name = "users/account.html"
    model = AppUser
    #changing from default object to user
    context_object_name = "user"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context["section"]="account"
        return context


class UpdateUserInfo(FormView):
    form_class = UserInfoForm
    template_name = "users/user_info_form.html"
    success_url = reverse_lazy("account")

    def get_initial(self):
        user=self.request.user
        initial=super().get_initial()
        initial['firstname'] = user.firstname
        initial['lastname'] = user.lastname
        initial['phone_number'] = user.phone_number

        return initial

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        user = self.request.user

        # Update user fields with the cleaned data from the form
        user.firstname = cleaned_data.get("firstname")
        user.lastname = cleaned_data.get("lastname")
        user.phone_number = cleaned_data.get("phone_number")

        # Save the updated user instance
        user.save()
        if self.request.headers.get("HX-Request"):
            return HttpResponse('<div class="alert alert-success">User information changed successfully!</div>')

        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get("HX-Request"):
            return self.render_to_response(self.get_context_data(form=form))

        return super().form_invalid(form)

class UpdateUserPassword(FormView):
    form_class = PasswordChangeForm
    template_name = 'users/password_change_form.html'  # Ensure this matches your template
    success_url = reverse_lazy('account')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass the current user to the form
        return kwargs

    def form_valid(self, form):
        user=self.request.user
        user.set_password(form.cleaned_data.get("new_password1"))
        user.save()
        update_session_auth_hash(self.request,user)

        if self.request.headers.get("HX-Request"):
            return HttpResponse('<div class="alert alert-success">Password changed successfully!</div>')
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get("HX-Request"):
            return self.render_to_response(self.get_context_data(form=form))

        return super().form_invalid(form)

def index(request):
    return render(request,"users/index.html")

class UserListView(ListView):
    model = AppUser  # Use the custom AppUser model
    template_name = 'users/user_list.html'  # Define your template path
    context_object_name = 'users'  # Name the conte

class UpdateEmailView(FormView):
    form_class = EmailChangeForm  # Corrected from 'form' to 'form_class'
    template_name = 'users/email_change_form.html'
    success_url = reverse_lazy("account")

    def form_valid(self, form):
        user = self.request.user
        new_email = form.cleaned_data.get("email1")
        user.email = new_email
        user.save()  # Don't forget to save the user with the new email
        if self.request.headers.get("HX-Request"):
            return HttpResponse('<div class="alert alert-success">Email changed successfully!</div>')
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get("HX-Request"):
            # Render the form with errors to be shown dynamically in the modal
            return self.render_to_response(self.get_context_data(form=form))

        return super().form_invalid(form)


