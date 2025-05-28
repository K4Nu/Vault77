from django.db.models import Prefetch
from rest_framework import viewsets,serializers
from .models import ProductItem, ProductImage, Category,ProductVariant
from .serializers import ProductItemSerializer, CategoryProductItemSerializer,CategorySerializer
from rest_framework.serializers import SerializerMethodField
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    SearchFilterBackend,
    OrderingFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from .documents import ProductItemDocument
from .serializers import ProductItemSearchSerializer

class ProductItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Each ProductItem is serialized with:
      - product__items → all_items  (all sibling items, color-select_related)
      - images → all_images         (to grab up to two images)
    """
    queryset = ProductItem.objects.select_related('product').prefetch_related(
        Prefetch(
            "product__items",
            queryset=ProductItem.objects.select_related('color'),
            to_attr="all_items"
        ),
        Prefetch("variants",
                 queryset=ProductVariant.objects.select_related("size").order_by('size__order'),to_attr="all_variants"),
        Prefetch(
            "images",
            queryset=ProductImage.objects.order_by("order"),
            to_attr="all_images"
        ),
    )
    serializer_class = ProductItemSerializer
    lookup_field = 'slug'

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Returns categories with their children and all associated product items.
    """
    queryset = Category.objects.prefetch_related(
        "children",
        "products",
        Prefetch(
            "products__items",
            queryset=ProductItem.objects
                .select_related("color")
                .prefetch_related(
                    Prefetch(
                        "images",
                        queryset=ProductImage.objects.order_by("order"),
                        to_attr="all_cat_images"
                    )
                ),
            to_attr="all_items"
        ),
    )
    serializer_class = CategorySerializer
    lookup_field = 'slug'

"""
Document views below
"""

class ProductItemSearchView(DocumentViewSet):
    document = ProductItemDocument
    serializer_class = ProductItemSearchSerializer

    filter_backends = [
        FilteringFilterBackend,
        SearchFilterBackend,
        OrderingFilterBackend,
    ]

    search_fields = ("product_name", "product_description")

    filter_fields = {
        'product_name': {
            'field': 'product_name.keyword',
            'lookups': ['term', 'prefix'],
        },
        'slug': {
            'field': 'slug',
            'lookups': ['term'],
        },
        "price":
            {
                "field":"price",
                "lookups":["term","range"]
            }
    }
    ordering_fields = {
        'product_name': 'product_name.keyword',
        'slug': 'slug',
        'price': 'price',
    }

    lookup_field = 'slug'
