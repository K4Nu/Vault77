from django.db import models
import json
from django.core.cache import cache

class Category(models.Model):
    name = models.CharField(max_length=100)
    parent_category = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)
    sizes = models.JSONField(blank=True, null=True, help_text="List of sizes applicable for this category.")

    def get_full_category_path(self):
        categories = []
        category = self
        while category:
            categories.append(category.name)
            category = category.parent_category
        return "/".join(reversed(categories))

    def __str__(self):
        return f'{self.get_full_category_path()}'

    @staticmethod
    def set_parent_category():
        # Retrieve top-level categories (those without a parent)
        parent_categories = Category.objects.filter(parent_category__isnull=True).values("name")
        # Convert to JSON and cache it
        json_parents = json.dumps(list(parent_categories))
        cache.set("parent_category", json_parents)
        return json_parents

    @staticmethod
    def get_parent_category():
        # Attempt to retrieve parent categories from the cache
        json_parents = cache.get("parent_category")
        # If not found in cache, set it using set_parent_category
        if json_parents is None:
            json_parents = Category.set_parent_category()
        return json.loads(json_parents)
