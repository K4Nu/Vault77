from django.shortcuts import render
from django.views.generic import CreateView
from .models import Category
from .forms import CategoryForm

class CreateCategoryView(CreateView):
    form_class = CategoryForm
    model = Category

    def form_valid(self, form):
        category = form.save(commit=False)
        category.save()

