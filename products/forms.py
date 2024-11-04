from django import forms
from .models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'parent_category', 'sizes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Retrieve top-level categories for the dropdown
        parent_categories = Category.objects.filter(parent_category__isnull=True).values("id", "name")

        # Set up the choices, using None as the value for "No Parent"
        choices = [(None, "No Parent")] + [(cat["id"], cat["name"]) for cat in parent_categories]

        # Update parent_category field to use ModelChoiceField
        self.fields['parent_category'] = forms.ModelChoiceField(
            queryset=Category.objects.filter(parent_category__isnull=True),
            required=False,
            empty_label="No Parent",
            label="Parent Category"
        )

    def save(self, commit=True):
        instance=super().save(commit=False)

        if self.cleaned_data['parent_category']:
            instance.sizes=self.cleaned_data['parent_category'].sizes

        if commit:
            instance.save()
        return instance
