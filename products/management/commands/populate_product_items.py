# products/management/commands/populate_product_items.py

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from products.models import Product, Color, ProductItem

class Command(BaseCommand):
    help = 'Populate a few product items for a specific product using preset colors.'

    def handle(self, *args, **options):
        # Change the product name below as needed.
        try:
            product = Product.objects.get(name="Classic Tee")
        except Product.DoesNotExist:
            self.stdout.write(self.style.ERROR("Product 'Kids Classic Tee' not found."))
            return

        # Manually specify the colors to use.
        color_names = ["Multicolor", "Red", "Black", "White"]

        for color_name in color_names:
            try:
                color = Color.objects.get(name=color_name)
            except Color.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Color '{color_name}' not found."))
                continue

            # Create the product item with a descriptive name.
            # The product_code and slug are handled automatically in the model's save() method.
            item_name = f"{product.name} - {color_name}"
            product_item, created = ProductItem.objects.get_or_create(
                product=product,
                color=color,
                defaults={
                    "name": item_name,
                    "price": 19.99,  # Adjust the price as needed.
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created product item: {item_name}"))
            else:
                self.stdout.write(f"Product item already exists: {item_name}")
