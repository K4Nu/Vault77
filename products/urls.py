from products import views as user_v
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("create-category/", user_v.CreateCategoryView.as_view(), name="create_category"),
    path("all-category/", user_v.CategoryListView.as_view(), name="all_category"),
    path("delete-category/<int:pk>", user_v.DeleteCategoryView.as_view(), name="delete_category"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)