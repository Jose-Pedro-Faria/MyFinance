from datetime import date
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.shortcuts import redirect, render

from .forms import SubCategoriaForm
from .models import Lancamento, Relatorio, SubCategoria

TIPOS = [
    ("REC", "Receita"),
    ("ESS", "Despesas Essenciais"),
    ("NES", "Despesas Não Essenciais"),
]


def _agrupar(subcategorias):
    return [
        {
            "cod": cod,
            "nome": nome,
            "categorias": [s for s in subcategorias if s.tipo == cod],
        }
        for cod, nome in TIPOS
    ]


def lista(request):
    grupos = _agrupar(SubCategoria.objects.all())

    linhas = []
    for r in Relatorio.objects.prefetch_related("lancamentos"):
        por_sub = {l.subcategoria_id: l.montante for l in r.lancamentos.all()}
        celulas = []
        totais = {}
        for g in grupos:
            valores = [por_sub.get(s.id) for s in g["categorias"]]
            soma = sum((v for v in valores if v is not None), Decimal("0"))
            celulas.append({"cod": g["cod"], "total": soma, "valores": valores})
            totais[g["cod"]] = soma
        linhas.append({
            "mes": r.mes,
            "grupos": celulas,
            "sobra": totais["REC"] - totais["ESS"] - totais["NES"],
        })

    return render(request, "relatorios/lista.html", {"grupos": grupos, "linhas": linhas})


def novo_relatorio(request):
    subcategorias = SubCategoria.objects.filter(ativa=True)
    grupos = _agrupar(subcategorias)
    erro = None

    if request.method == "POST":
        try:
            ano, mes = request.POST["mes"].split("-")
            data = date(int(ano), int(mes), 1)
            valores = {}
            for s in subcategorias:
                bruto = request.POST.get(f"sub_{s.id}", "").strip().replace(",", ".")
                if bruto:
                    valores[s] = Decimal(bruto)
        except (ValueError, InvalidOperation, KeyError):
            erro = "Verifica o mês e os valores introduzidos."
        else:
            with transaction.atomic():
                relatorio, _ = Relatorio.objects.get_or_create(mes=data)
                for s, montante in valores.items():
                    Lancamento.objects.update_or_create(
                        relatorio=relatorio, subcategoria=s,
                        defaults={"montante": montante},
                    )
            return redirect("relatorios:lista")

    return render(request, "relatorios/novo.html", {
        "grupos": grupos,
        "erro": erro,
        "hoje": date.today(),
    })


def nova_subcategoria(request):
    form = SubCategoriaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("relatorios:novo")
    return render(request, "relatorios/subcategoria.html", {"form": form})