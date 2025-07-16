from django.db.models import Prefetch
from rest_framework import viewsets, serializers, permissions
from rest_framework.permissions import AllowAny
from .models import ProductItem, ProductImage, Category,ProductVariant
from .serializers import ProductItemSerializer, CategoryProductItemSerializer,CategorySerializer
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    SearchFilterBackend,
    OrderingFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from .serializers import ProductItemSearchSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q
from django_elasticsearch_dsl.documents import Document
from elasticsearch_dsl.connections import connections
from .documents import ProductItemDocument


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

class ProductItemSuggestView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        q = request.GET.get("q", "")
        suggestions = []

        if q:
            s = ProductItemDocument.search()
            s = s.suggest(
                "product-suggest",
                q,
                completion={"field": "product_name_suggest", "size": 10}  # allow more to deduplicate
            )
            response = s.execute()
            seen = set()

            for option in response.suggest["product-suggest"][0]["options"]:
                text = option["text"]
                if text not in seen:
                    seen.add(text)
                    suggestions.append(text)
                if len(suggestions) >= 5:
                    break

        return Response(suggestions)

class FullProductItemSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "")
        if not query:
            return Response([])

        # 1. Search in Elasticsearch
        s = ProductItemDocument.search()
        s = s.query("multi_match", query=query, fields=["product_name", "product_description"])
        results = s.execute()
        print("Elasticsearch hits:", [hit.slug for hit in results])
        # 2. Get slugs from ES
        slugs = [hit.slug for hit in results]

        # 3. Fetch matching ORM objects using prefetch
        items = ProductItem.objects.select_related("color").prefetch_related(
            Prefetch(
                "images",
                queryset=ProductImage.objects.order_by("order"),
                to_attr="all_cat_images"
            )
        ).filter(slug__in=slugs)

        # 4. Serialize using your rich CategoryProductItemSerializer
        serializer = CategoryProductItemSerializer(items, many=True, context={"request": request})
        return Response(serializer.data)