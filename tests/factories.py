import io

import factory
from django.core.files.base import ContentFile
from PIL import Image

from apps.catalogo.models import Category, Collection, Product, ProductImage, Variant

SCHEMA_GOTEJO = [
    {"key": "material", "label": "Material", "type": "choice", "choices": ["PE", "PP"]},
    {"key": "autocompensante", "label": "Autocompensante", "type": "boolean"},
    {"key": "pressao_max", "label": "Pressão máxima", "type": "number", "unit": "bar", "required": True},
    {"key": "vazao", "label": "Vazão", "type": "number", "unit": "L/h", "variant": True},
]


def png(cor=(29, 106, 68), tamanho=(120, 120)) -> ContentFile:
    buf = io.BytesIO()
    Image.new("RGB", tamanho, cor).save(buf, format="PNG")
    return ContentFile(buf.getvalue(), name="teste.png")


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Categoria {n}")
    attribute_schema = factory.LazyFunction(list)


class CollectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Collection

    name = factory.Sequence(lambda n: f"Coleção {n}")


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
        skip_postgeneration_save = True

    name = factory.Sequence(lambda n: f"Produto {n}")
    sku = factory.Sequence(lambda n: f"SKU-{n:04d}")
    primary_category = factory.SubFactory(CategoryFactory)
    short_description = "Descrição curta de teste."

    @factory.post_generation
    def categorias(self, create, extracted, **kwargs):
        if create:
            self.ensure_primary_in_categories()
            for cat in extracted or []:
                self.categories.add(cat)


class VariantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Variant

    product = factory.SubFactory(ProductFactory)
    sku = factory.Sequence(lambda n: f"VAR-{n:04d}")


class ProductImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductImage

    product = factory.SubFactory(ProductFactory)
    image = factory.LazyFunction(png)
