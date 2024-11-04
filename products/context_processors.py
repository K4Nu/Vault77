from django.core.cache import cache

def cached_queries():
    return {"cached_queries": cache.get("category_parents")}