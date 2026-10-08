from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import InvestimentoForm
from .models import Captura, CapturaItem, Categoria, Investimento


def _agrupar(itens):
    """Agrupa posições por categoria e calcula subtotais e total geral."""
    grupos = []
    total = Decimal("0")
    for cod, nome in Categoria.choices:
        do_grupo = [i for i in itens if i.categoria == cod]
        subtotal = sum((i.valor_total for i in do_grupo), Decimal("0"))
        total += subtotal
        grupos.append({"cod": cod, "nome": nome, "itens": do_grupo, "subtotal": subtotal})
    return grupos, total


# ---------- Posições atuais ----------

def lista(request):
    investimentos = list(Investimento.objects.all())
    grupos, total_geral = _agrupar(investimentos)
    return render(request, "investimentos/lista.html", {
        "grupos": grupos,
        "total_geral": total_geral,
        "tem_posicoes": bool(investimentos),
    })


def editar(request, pk=None):
    investimento = get_object_or_404(Investimento, pk=pk) if pk else None
    initial = {} if investimento else {"categoria": request.GET.get("categoria")}
    form = InvestimentoForm(request.POST or None, instance=investimento, initial=initial)
    if form.is_valid():
        form.save()
        return redirect("investimentos:lista")
    return render(request, "investimentos/form.html", {
        "form": form,
        "investimento": investimento,
    })


@require_POST
def apagar(request, pk):
    get_object_or_404(Investimento, pk=pk).delete()
    return redirect("investimentos:lista")


# ---------- Capturas (histórico) ----------

@require_POST
def capturar(request):
    investimentos = Investimento.objects.all()
    if not investimentos:
        return redirect("investimentos:lista")

    with transaction.atomic():
        nova = Captura.objects.create(nota=request.POST.get("nota", "").strip()[:200])
        CapturaItem.objects.bulk_create([
            CapturaItem(
                captura=nova,
                categoria=i.categoria,
                nome=i.nome,
                unidades=i.unidades,
                valor_unitario=i.valor_unitario,
                corretora=i.corretora,
            )
            for i in investimentos
        ])
    return redirect("investimentos:captura", pk=nova.pk)


def historico(request):
    linhas = []
    for c in Captura.objects.prefetch_related("itens"):
        grupos, total = _agrupar(list(c.itens.all()))
        linhas.append({
            "captura": c,
            "subtotais": [g["subtotal"] for g in grupos],
            "total": total,
        })
    return render(request, "investimentos/historico.html", {
        "categorias": [nome for _, nome in Categoria.choices],
        "linhas": linhas,
    })


def captura(request, pk):
    c = get_object_or_404(Captura, pk=pk)
    grupos, total_geral = _agrupar(list(c.itens.all()))
    return render(request, "investimentos/captura.html", {
        "captura": c,
        "grupos": grupos,
        "total_geral": total_geral,
    })


@require_POST
def apagar_captura(request, pk):
    get_object_or_404(Captura, pk=pk).delete()
    return redirect("investimentos:historico")