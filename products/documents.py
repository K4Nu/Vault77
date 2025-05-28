from django_elasticsearch_dsl import Document,fields
from django_elasticsearch_dsl.registries import registry
from products.models import ProductItem

@registry.register_document
class ProductItemDocument(Document):
    product_name = fields.TextField(attr="product_name")
    product_description = fields.TextField(attr="product_description")
    price = fields.ScaledFloatField(scaling_factor=100)

    class Index:
        name = 'productitems'

    class Django:
        model = ProductItem
        fields = ("slug",)