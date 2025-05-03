# products/management/commands/populate_categories.py

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from products.models import Gender, Category, SizeGroup

class Command(BaseCommand):
    help = 'Populate the Category model with default entries for each gender.'

    def handle(self, *args, **options):
        # Define the categories and size_group mapping for each gender.
        categories_data = {
            "Kids": {
                "size_group": "Children Clothes",
                "categories": ["Tops", "Bottoms", "Outerwear", "Footwear", "Accessories"],
            },
            "Women": {
                "size_group": "Women Trousers",  # Adjust if needed (or use "Adult Clothes" if preferred)
                "categories": ["Dresses", "Tops", "Bottoms", "Shoes", "Accessories"],
            },
            "Men": {
                "size_group": "Men Trousers",  # Adjust if needed (or use "Adult Clothes" if preferred)
                "categories": ["Suits", "Shirts", "Trousers", "Shoes", "Accessories"],
            },
        }

        for gender_name, data in categories_data.items():
            # Get or create the Gender object.
            gender, created = Gender.objects.get_or_create(name=gender_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Gender: {gender_name}"))
            else:
                self.stdout.write(f"Gender already exists: {gender_name}")

            # Get or create the SizeGroup object.
            size_group_name = data["size_group"]
            size_group, sg_created = SizeGroup.objects.get_or_create(
                name=size_group_name,
                defaults={'slug': slugify(size_group_name)}
            )
            if sg_created:
                self.stdout.write(self.style.SUCCESS(f"Created SizeGroup: {size_group_name}"))
            else:
                self.stdout.write(f"SizeGroup already exists: {size_group_name}")

            # For each category name defined, create a Category object.
            for cat_name in data["categories"]:
                # Check if a category already exists for this gender and with this name.
                category, cat_created = Category.objects.get_or_create(
                    name=cat_name,
                    gender=gender,
                    size_group=size_group,
                    parent=None,  # Assuming top-level categories
                    defaults={'slug': slugify(f"{gender.name}-{cat_name}")}  # Temporary slug; will update via save() if needed
                )
                if cat_created:
                    self.stdout.write(self.style.SUCCESS(f"Created Category '{cat_name}' for Gender '{gender_name}'"))
                else:
                    self.stdout.write(f"Category '{cat_name}' for Gender '{gender_name}' already exists")
