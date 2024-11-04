from django.forms import forms
from .models import Category

class CategoryForm(forms.Form):
    class Meta:
        name=Category
        fields = ['name', 'parent_category', 'sizes']

    def __init__(self, *args, **kwargs):
        super(self).__init__(*args, **kwargs)

        parent_categories=Category.get_parent_category()
        choices = [(None, "No Parent")] + [(cat["id"], cat["name"]) for cat in parent_categories]
        self.fields['parent_category'] = forms.ChoiceField(
            choices=choices,
            required=False,
            label="Parent Category",
        )

