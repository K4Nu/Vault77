from django.shortcuts import render
from django.http import HttpResponse
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from .models import AppUser

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