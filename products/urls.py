from . import views
from django.urls import path

urlpatterns = [
    #path("", views.ProductListView.as_view(), name="product_list"),
    path("category/", views.CategoryListView.as_view(), name="category"),
    path("create-category/", views.CreateCategoryView.as_view(), name="create-category"),
]