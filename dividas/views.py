from decimal import Decimal

from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import DividaForm
from .models import Divida


def lista(request):
    dividas = list(Divida.objects.all())
    ativas = [d for d in dividas if d.meses_em_falta > 0]
    mensalidade_total = sum((d.mensalidade for d in ativas), Decimal("0"))
    divida_total = sum((d.total_em_falta for d in ativas), Decimal("0"))
    return render(request, "dividas/lista.html", {
        "dividas": dividas,
        "mensalidade_total": mensalidade_total,
        "divida_total": divida_total,
    })


def editar(request, pk=None):
    divida = get_object_or_404(Divida, pk=pk) if pk else None
    form = DividaForm(request.POST or None, instance=divida)
    if form.is_valid():
        form.save()
        return redirect("dividas:lista")
    return render(request, "dividas/form.html", {"form": form, "divida": divida})


@require_POST
def apagar(request, pk):
    get_object_or_404(Divida, pk=pk).delete()
    return redirect("dividas:lista")