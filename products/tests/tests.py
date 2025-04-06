import pytest
from products.models import Gender,Category,SizeGroup,Size,Product,ProductItem,Color

@pytest.fixture
def men(db):
    return Gender.objects.create(gender_name='Men')

@pytest.fixture
def category(db):
    # Using a separate Gender instance here; adjust as needed.
    return Category.objects.create(name='Test', gender=Gender.objects.create(gender_name='Temp'))

@pytest.fixture
def size_group(db, category):
    return SizeGroup.objects.create(name='Test', category=category)

@pytest.fixture
def color(db):
    return Color.objects.create(name='Red')

@pytest.fixture
def product(db, category):
    return Product.objects.create(name='Test', category=category)

@pytest.mark.django_db
class TestGenderModel:
    def test_str_method(self):
        gender = Gender.objects.create(gender_name='male')
        assert str(gender) == 'male'

@pytest.mark.django_db
class TestCategoryModel:
    def test_str_method(self, men):
        # Create a chain of categories to test the __str__ method.
        c1 = Category.objects.create(name='cat1', gender=men)
        c2 = Category.objects.create(name='cat2', gender=men, parent=c1)
        c3 = Category.objects.create(name='cat3', gender=men, parent=c2)
        assert str(c3) == "cat1 > cat2 > cat3"

    def test_get_queryset_filters_out_child_categories(self, men):
        # Create a top-level (parent) category.
        parent = Category.objects.create(name='Parent', gender=men)
        # Create a child category whose parent is the above category.
        child = Category.objects.create(name='Child', parent=parent, gender=men)
        # Use the custom manager (all_objects) that filters out child categories.
        qs = Category.all_objects.all()
        # Verify that the parent category is included.
        assert parent in qs, "Parent category should be returned by the custom manager."
        # Verify that the child category is excluded.
        assert child not in qs, "Child category should not be returned by the custom manager."
        # Ensure that exactly one category is returned.
        assert qs.count() == 1

@pytest.mark.django_db
class TestSizeGroupModel:
    def test_str_method(self, men, category):
        size_group = SizeGroup.objects.create(name='Adults Normal', category=category)
        assert str(size_group) == 'Adults Normal'

    def test_slug(self, category):
        size_group = SizeGroup.objects.create(name='Adults Normal', category=category)
        assert size_group.slug == 'adults-normal'

@pytest.mark.django_db
class TestSizeModel:
    def test_str_method(self, size_group):
        size = Size.objects.create(name='XL', size_group=size_group)
        # The __str__ method returns: size_group.name + ' - ' + size.name
        expected_str = f"{size_group.name} - {size.name}"
        assert str(size) == expected_str

@pytest.mark.django_db
class TestProductModel:
    def test_str_method(self,category):
        product=Product.objects.create(name='Test', category=category)
        assert str(product) == f'{category} - Test'

@pytest.mark.django_db
class TestProductItemModel:
    def test_str_method(self, product, color):
        item=ProductItem.objects.create(name='Test',product=product, color=color, product_code="#123")
        assert str(item) == "Test - #123"

        assert item.slug == "123"