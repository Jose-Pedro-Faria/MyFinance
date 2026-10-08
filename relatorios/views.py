from datetime import date
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.shortcuts import redirect, render

from .forms import SubCategoriaForm
from .models import Lancamento, Relatorio, SubCategoria

from config.calculos import calcular

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
    subcategorias = list(SubCategoria.objects.filter(ativa=True))
    grupos = _agrupar(subcategorias)
    erro = None

    mes_txt = request.POST.get("mes") or request.GET.get("mes") or date.today().strftime("%Y-%m")
    try:
        ano, mes = mes_txt.split("-")
        data = date(int(ano), int(mes), 1)
    except ValueError:
        data = date.today().replace(day=1)
        mes_txt = data.strftime("%Y-%m")

    if request.method == "POST":
        digitado = {s.id: request.POST.get(f"sub_{s.id}", "").strip() for s in subcategorias}
        try:
            valores = {
                s: (calcular(digitado[s.id]), digitado[s.id])
                for s in subcategorias if digitado[s.id]
            }
        except (ValueError, SyntaxError, InvalidOperation, ZeroDivisionError):
            erro = "Há um valor inválido. Usa números e as operações + - * / (ex.: 50+20+100)."
        else:
            with transaction.atomic():
                relatorio, _ = Relatorio.objects.get_or_create(mes=data)
                for s, (montante, expressao) in valores.items():
                    Lancamento.objects.update_or_create(
                        relatorio=relatorio, subcategoria=s,
                        defaults={"montante": montante, "expressao": expressao},
                    )
                vazias = [s for s in subcategorias if not digitado[s.id]]
                Lancamento.objects.filter(
                    relatorio=relatorio, subcategoria__in=vazias
                ).delete()
            return redirect("relatorios:lista")
    else:
        existentes = Lancamento.objects.filter(relatorio__mes=data)
        digitado = {l.subcategoria_id: (l.expressao or str(l.montante)) for l in existentes}

    for s in subcategorias:
        s.valor_atual = digitado.get(s.id, "")

    return render(request, "relatorios/novo.html", {
        "grupos": grupos,
        "erro": erro,
        "mes_txt": mes_txt,
    })


def nova_subcategoria(request):
    form = SubCategoriaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("relatorios:novo")
    return render(request, "relatorios/subcategoria.html", {"form": form})