from django.contrib import admin
from .models import SubCategoria, Relatorio, Lancamento


class LancamentoInline(admin.TabularInline):
    model = Lancamento
    extra = 0


@admin.register(Relatorio)
class RelatorioAdmin(admin.ModelAdmin):
    inlines = [LancamentoInline]


admin.site.register(SubCategoria)