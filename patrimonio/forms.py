from django import forms
from .models import Categoria


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nome", "grupo"]

class CategoriaNomeForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nome"]