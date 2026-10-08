from django import forms
from .models import SubCategoria


class SubCategoriaForm(forms.ModelForm):
    class Meta:
        model = SubCategoria
        fields = ["nome", "tipo"]