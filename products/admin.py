from django.contrib import admin
from products.models import (
    Product,
    ProductItem,
    ProductImage,
    Size,
    SizeGroup,
    ProductVariant,
    Color,
    Category,
    Gender
)


from mptt.admin import DraggableMPTTAdmin

# Register Category with a tree admin display
@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "name"
    list_display = ('tree_actions', 'indented_title', 'gender',)
    list_display_links = ('indented_title',)

# Register the Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category',)
    prepopulated_fields = {"slug": ("name",)}

# Register the ProductItem model
@admin.register(ProductItem)
class ProductItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'color', 'price', 'product_code', 'slug',)
    prepopulated_fields = {"slug": ("product_code",)}

# Register the ProductImage model
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('name', 'item', 'order', 'created_at', 'updated_at',)
    prepopulated_fields = {"slug": ("name",)}

# Register the Size model
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'size_group', 'order',)

# Register the SizeGroup model
@admin.register(SizeGroup)
class SizeGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {"slug": ("name",)}

# Register the ProductVariant model
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product_item', 'size', 'quantity',)

# Register the Color model
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name',)

# Register the Gender model
@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ('name',)