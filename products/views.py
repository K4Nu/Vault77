from django.shortcuts import render, redirect
from django.views.generic import CreateView, ListView
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from .forms import CategoryForm
from .models import Product, Category, ProductImage


class CreateCategoryView(UserPassesTestMixin, CreateView):
    model = Category  # Remove quotes, it should be the actual model class
    template_name = 'products/category_form.html'
    form_class = CategoryForm

    def test_func(self):
        # Check if user is superuser or staff
        return self.request.user.is_authenticated and (self.request.user.is_superuser or self.request.user.is_staff)

    def dispatch(self, request, *args, **kwargs):
        # Need to call parent's dispatch
        if not self.test_func():
            messages.error(request, 'You are not authorized to create categories.')
            return redirect('products:show-category')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        name = form.cleaned_data.get('name')
        parent = form.cleaned_data.get('parent')

        # This check isn't necessary since we're using a ModelForm
        # The parent validation is handled by the form itself
        category = form.save()  # Save the form directly

        messages.success(self.request, f'Category "{category.name}" created successfully.')
        return redirect("products:show-category")

    def form_invalid(self, form):
        messages.error(self.request, 'Error creating category. Please check the form.')
        return super().form_invalid(form)


class CategoryListView(ListView):
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        # Get main categories (Men, Women, Kids) first
        main_categories = Category.objects.filter(parent=None, is_gender_category=True)

        # For each main category, we'll get its subcategories
        categories_dict = {}
        for main_cat in main_categories:
            subcategories = Category.objects.filter(parent=main_cat)
            categories_dict[main_cat] = subcategories

        return categories_dict

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Categories'
        return context
