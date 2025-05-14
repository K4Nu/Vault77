from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from products.models import ProductItem, ProductImage, Color, Category


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ('id', 'name', 'hex_code')


class ProductItemImageSerializer(serializers.ModelSerializer):
    url = SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ('url',)

    def get_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.filename.url)


class ProductItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    colors       = SerializerMethodField()
    images       = SerializerMethodField()

    class Meta:
        model  = ProductItem
        fields = ("product_name", "slug", "price", "colors", "images")

    def get_colors(self, obj):
        # Prefer the cached list of sibling items, fallback to DB
        siblings = getattr(obj.product, 'all_items', None)
        if siblings is None:
            siblings = obj.product.items.select_related('color').all()

        seen = {}
        # Always include current item's color first
        if obj.color:
            seen[obj.color.id] = obj.color

        for item in siblings:
            if item.color and item.color.id not in seen:
                seen[item.color.id] = item.color

        return ColorSerializer(list(seen.values()), many=True, context=self.context).data

    def get_images(self, obj):
        # Return up to the first two prefetched images
        imgs = getattr(obj, 'all_images', [])[:2]
        return ProductItemImageSerializer(imgs, many=True, context=self.context).data


class CategorySerializer(serializers.ModelSerializer):
    children = SerializerMethodField()
    items    = SerializerMethodField()

    class Meta:
        model  = Category
        fields = ('id', 'name', 'slug', 'children', 'items')

    def get_children(self, obj):
        return CategorySerializer(
            obj.children.all(),
            many=True,
            context=self.context
        ).data

    def get_items(self, obj):
        # Flatten all items from each product, using prefetched "all_items"
        all_items = []
        for product in obj.products.all():
            all_items.extend(getattr(product, 'all_items', []))
        return ProductItemSerializer(all_items, many=True, context=self.context).data
