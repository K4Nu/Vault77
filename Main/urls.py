"""
URL configuration for Main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from products.views import ProductItemViewSet,CategoryViewSet,ProductItemSearchView,ProductItemSuggestView,FullProductItemSearchView
from django.conf import settings
from django.conf.urls.static import static
from debug_toolbar.toolbar import debug_toolbar_urls
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from products import views as product_views
router=DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductItemViewSet, basename='product')
router.register(r'search/product-items', ProductItemSearchView, basename='productitem-search')

urlpatterns = [
    path('admin/', admin.site.urls),
    path("silk/", include("silk.urls")),
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/register", include("dj_rest_auth.registration.urls")),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path("api/suggest/product-items/", ProductItemSuggestView.as_view(), name="productitem-suggest"),
    path("api/full-search/",FullProductItemSearchView.as_view(), name="full-product-search"),
    path("api/", include(router.urls)),
]+ debug_toolbar_urls()
if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)