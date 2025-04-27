from django.core.management.base import BaseCommand
from products.models import Product, Category

class Command(BaseCommand):
    help = 'Populate the database with 5 sample products assigned to specific, relevant categories'

    def handle(self, *args, **options):
        # Get the categories manually
        try:
            # For Kids, we need a top category (e.g., "Tops" for Kids)
            kids_top = Category.objects.get(name="Tops", gender__name="Kids")
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR("Category 'Tops' for Kids not found."))
            return

        try:
            # For Women, get the "Dresses" category
            women_dresses = Category.objects.get(name="Dresses", gender__name="Women")
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR("Category 'Dresses' for Women not found."))
            return

        try:
            # For Men, get the "Suits" category
            men_suits = Category.objects.get(name="Suits", gender__name="Men")
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR("Category 'Suits' for Men not found."))
            return

        try:
            # For Men, get the "Shirts" category
            men_shirts = Category.objects.get(name="Shirts", gender__name="Men")
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR("Category 'Shirts' for Men not found."))
            return

        try:
            # For Women, get the "Shoes" category
            women_shoes = Category.objects.get(name="Shoes", gender__name="Women")
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR("Category 'Shoes' for Women not found."))
            return

        # Now manually create each product

        # Product 1: Kids Classic Tee in Kids Tops category
        product1, created1 = Product.objects.get_or_create(
            name="Classic Tee",
            category=kids_top,
            defaults={
                "description": "A comfortable classic tee designed for kids.",
                "care_instructions": "Machine wash cold.",
            }
        )
        if created1:
            self.stdout.write(self.style.SUCCESS("Created product: Kids Classic Tee"))
        else:
            self.stdout.write("Product already exists: Kids Classic Tee")

        # Product 2: Elegant Dress in Women Dresses category
        product2, created2 = Product.objects.get_or_create(
            name="Elegant Dress",
            category=women_dresses,
            defaults={
                "description": "A stylish, elegant dress suitable for formal occasions.",
                "care_instructions": "Dry clean only.",
            }
        )
        if created2:
            self.stdout.write(self.style.SUCCESS("Created product: Elegant Dress"))
        else:
            self.stdout.write("Product already exists: Elegant Dress")

        # Product 3: Formal Suit in Men Suits category
        product3, created3 = Product.objects.get_or_create(
            name="Formal Suit",
            category=men_suits,
            defaults={
                "description": "A sleek and modern suit for professional settings.",
                "care_instructions": "Dry clean only.",
            }
        )
        if created3:
            self.stdout.write(self.style.SUCCESS("Created product: Formal Suit"))
        else:
            self.stdout.write("Product already exists: Formal Suit")

        # Product 4: Casual Shirt in Men Shirts category
        product4, created4 = Product.objects.get_or_create(
            name="Casual Shirt",
            category=men_shirts,
            defaults={
                "description": "A casual shirt perfect for everyday wear.",
                "care_instructions": "Machine wash warm.",
            }
        )
        if created4:
            self.stdout.write(self.style.SUCCESS("Created product: Casual Shirt"))
        else:
            self.stdout.write("Product already exists: Casual Shirt")

        # Product 5: Stylish Heels in Women Shoes category
        product5, created5 = Product.objects.get_or_create(
            name="Stylish Heels",
            category=women_shoes,
            defaults={
                "description": "Elegant and fashionable heels for special occasions.",
                "care_instructions": "Handle with care.",
            }
        )
        if created5:
            self.stdout.write(self.style.SUCCESS("Created product: Stylish Heels"))
        else:
            self.stdout.write("Product already exists: Stylish Heels")
