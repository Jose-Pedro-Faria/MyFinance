from django.contrib import admin
from .models import Categoria, RegistoMensal, Valor


class ValorInline(admin.TabularInline):
    model = Valor
    extra = 0


@admin.register(RegistoMensal)
class RegistoMensalAdmin(admin.ModelAdmin):
    inlines = [ValorInline]


admin.site.register(Categoria)