from django import forms

from products.models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'parent']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get only the main gender categories (Men, Women, Kids) for parent choices
        main_categories = Category.objects.filter(parent=None, is_gender_category=True)
        self.fields['parent'].queryset = main_categories
        self.fields['parent'].required = True  # Make parent required since all products must be under a gender