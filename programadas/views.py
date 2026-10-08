from datetime import date
from decimal import Decimal

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import DespesaForm
from .models import DespesaProgramada


def lista(request):
    todos = bool(request.GET.get("todos"))

    por_mes = {}
    for d in DespesaProgramada.objects.all():
        por_mes.setdefault((d.data.year, d.data.month), []).append(d)

    cards = []
    for (ano, mes), itens in sorted(por_mes.items()):
        completo = all(i.paga for i in itens)
        if completo and not todos:
            continue
        cards.append({
            "mes": date(ano, mes, 1),
            "itens": itens,
            "completo": completo,
            "total": sum((i.valor for i in itens), Decimal("0")),
            "pendente": sum((i.valor for i in itens if not i.paga), Decimal("0")),
        })

    return render(request, "programadas/lista.html", {"cards": cards, "todos": todos})


def editar(request, pk=None):
    despesa = get_object_or_404(DespesaProgramada, pk=pk) if pk else None
    form = DespesaForm(request.POST or None, instance=despesa)
    if form.is_valid():
        form.save()
        return redirect("programadas:lista")
    return render(request, "programadas/form.html", {"form": form, "despesa": despesa})


@require_POST
def apagar(request, pk):
    get_object_or_404(DespesaProgramada, pk=pk).delete()
    return redirect("programadas:lista")


@require_POST
def alternar(request, pk):
    despesa = get_object_or_404(DespesaProgramada, pk=pk)
    despesa.paga = request.POST.get("paga") == "on"
    despesa.save(update_fields=["paga"])
    destino = reverse("programadas:lista")
    if request.POST.get("todos"):
        destino += "?todos=1"
    return redirect(destino)