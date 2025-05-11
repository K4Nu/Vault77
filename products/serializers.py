from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from products.models import ProductItem, ProductImage, Color

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Color
        fields = ('id', 'name', 'hex_code')

class ProductItemImageSerializer(serializers.ModelSerializer):
    url = SerializerMethodField()

    class Meta:
        model  = ProductImage
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
        """
        Start with the current item's color, then append each sibling's
        color (no duplicates), in the order they were prefetched.
        """
        siblings   = getattr(obj.product, 'all_items', [])
        curr_color = obj.color

        seen = {}
        if curr_color:
            seen[curr_color.id] = curr_color

        for item in siblings:
            color = item.color
            if color and color.id not in seen:
                seen[color.id] = color

        return ColorSerializer(list(seen.values()), many=True, context=self.context).data

    def get_images(self, obj):
        """
        Return up to the first two images from the prefetched all_images.
        """
        imgs = getattr(obj, 'all_images', [])[:2]
        return ProductItemImageSerializer(imgs, many=True, context=self.context).data