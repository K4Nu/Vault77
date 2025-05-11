# views.py


from django.db.models import OuterRef, Subquery, Prefetch
from rest_framework import viewsets
from .models import ProductItem, ProductImage,Color,Category
from .serializers import ProductItemSerializer,CategorySerializer

class ProductItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductItem.objects.select_related('product').prefetch_related(
        Prefetch("product__items",queryset=ProductItem.objects.select_related('color'),to_attr="all_items"),
        Prefetch("images",queryset=ProductImage.objects.order_by("order"),to_attr="all_images")
    )
    serializer_class = ProductItemSerializer

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Category.objects
        .prefetch_related(
            "children",
            "products",
            # ONE Prefetch for products__items that itself prefetches images
            Prefetch(
                "products__items",
                queryset=ProductItem.objects
                    .select_related("color")
                    .prefetch_related(
                        Prefetch(
                            "images",
                            queryset=ProductImage.objects.order_by("order"),
                            to_attr="all_images"
                        )
                    ),
                to_attr="related_items"
            ),
        )
    )
    serializer_class = CategorySerializer
    lookup_field = 'slug'