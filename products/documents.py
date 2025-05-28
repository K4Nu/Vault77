from django_elasticsearch_dsl import Document,fields
from django_elasticsearch_dsl.registries import registry
from products.models import ProductItem
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer, tokenizer

autocomplete_analyzer=analyzer(
    'automcomplete',
    okenizer=tokenizer('edge_ngram_tokenizer', 'edge_ngram', min_gram=1, max_gram=20),
    filter=['lowercase']
)

autocomplete_search_analyzer=analyzer(
    'autocomplete_search',
    tokenizer=["standard"],
    filter=['lowercase']
)


@registry.register_document
class ProductItemDocument(Document):
    product_name = fields.TextField(attr="product_name",
                                    analyzer=autocomplete_analyzer,
                                    search_analyzer=autocomplete_search_analyzer,)
    product_description = fields.TextField(attr="product_description")
    price = fields.ScaledFloatField(scaling_factor=100)
    product_name_suggest=fields.CompletionField()

    class Index:
        name = 'productitems'

    class Django:
        model = ProductItem
        fields = ("slug",)

    def prepare_product_name_suggest(self,instance):
        return instance.product.name