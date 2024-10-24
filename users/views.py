from django.shortcuts import render
from django.urls import reverse_lazy,reverse
from django.http import HttpResponse
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, UpdateView, FormView,ListView
from .models import AppUser
from .forms import PasswordChangeForm
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

class UpdateUserInfo(UpdateView):
    model = AppUser
    fields = ['firstname', 'lastname', 'phone_number']
    success_url = reverse_lazy('account')  # Redirect to the account page after successful update

    def get_object(self):
        # Ensure that only the current logged-in user can edit their profile
        return self.request.user

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