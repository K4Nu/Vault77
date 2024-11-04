from django.views.generic import CreateView, ListView, DetailView, DeleteView
from .models import Category
from .forms import CategoryForm
from django.urls import reverse_lazy,reverse

class CreateCategoryView(CreateView):
    form_class = CategoryForm
    model = Category
    template_name = "products/create_category.html"
    success_url = reverse_lazy("create_category")

    def form_valid(self, form):
        category = form.save(commit=False)
        category.save()  # Save the category instance
        return super().form_valid(form)

class CategoryListView(ListView):
    model = Category
    template_name = "products/products_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        # Only fetch top-level categories (those without a parent)
        #where parent in (...)
        return Category.objects.filter(parent_category__isnull=True).prefetch_related('category_set')

class CategoryDetailView(DetailView):
    pass

class DeleteCategoryView(DeleteView):
    model = Category
    success_url = reverse_lazy("all_category")

    def get(self, request, *args, **kwargs):
        # Immediately delete the object without rendering a confirmation page
        return self.post(request, *args, **kwargs)