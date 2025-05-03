from django.core.management.base import BaseCommand
from products.models import ProductItem, ProductVariant, Size, SizeGroup


class Command(BaseCommand):
    help = 'Create variants for specific ProductItems'

    def handle(self, *args, **kwargs):
        # Hoodie variants
        hoodie_items = {
            "84c1a5b773934cc8a1830380ec0d4dce": ["XS", "S", "M", "L", "XL"],  # Blue
            "36cee1e47b924918b69cd54cbdb4282d": ["M", "L"],                  # Grey
            "54f17dfd48cd4aa08a65cc093268d7c5": ["XS", "S", "M", "L", "XL"], # Magenta
        }

        shoe_item_code = "17edcaa032eb4c3dae10faaf3545ace8"
        shoe_sizes = ["40", "41", "42", "43", "44", "45"]

        try:
            adult_group = SizeGroup.objects.get(name="Adult Clothes")
            shoe_group = SizeGroup.objects.get(name="Shoes")
        except SizeGroup.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f"SizeGroup missing: {e}"))
            return

        # Create hoodie variants
        for code, sizes in hoodie_items.items():
            try:
                item = ProductItem.objects.get(product_code=code)
            except ProductItem.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"ProductItem not found: {code}"))
                continue

            for size in Size.objects.filter(size_group=adult_group, name__in=sizes):
                variant, created = ProductVariant.objects.get_or_create(
                    product_item=item,
                    size=size,
                    defaults={"quantity": 10}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created hoodie variant: {item} - {size.name}"))
                else:
                    self.stdout.write(f"Hoodie variant exists: {item} - {size.name}")

        # Create sneaker variants
        try:
            sneaker_item = ProductItem.objects.get(product_code=shoe_item_code)
        except ProductItem.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Sneaker ProductItem not found: {shoe_item_code}"))
            return

        for size in Size.objects.filter(size_group=shoe_group, name__in=shoe_sizes):
            variant, created = ProductVariant.objects.get_or_create(
                product_item=sneaker_item,
                size=size,
                defaults={"quantity": 15}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created sneaker variant: {sneaker_item} - {size.name}"))
            else:
                self.stdout.write(f"Sneaker variant exists: {sneaker_item} - {size.name}")
