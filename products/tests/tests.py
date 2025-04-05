import pytest
from products.models import Gender,Category

@pytest.fixture
def men(db):
    return Gender.objects.create(gender_name='Men')

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