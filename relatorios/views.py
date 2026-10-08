from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from datetime import date

from config.calculos import calcular
from config.datas import MESES, anos_disponiveis, ler_mes

from .forms import SubCategoriaForm
from .models import Lancamento, Relatorio, SubCategoria

TIPOS = [
    ("REC", "Receita"),
    ("ESS", "Despesas Essenciais"),
    ("NES", "Despesas Não Essenciais"),
    ("INV", "Investimento"),
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
            "pk": r.pk,
            "mes": r.mes,
            "grupos": celulas,
            "sobra": totais["REC"] - totais["ESS"] - totais["NES"] - totais["INV"],
        })

    return render(request, "relatorios/lista.html", {"grupos": grupos, "linhas": linhas})


# ---------- Funções de apoio ao formulário ----------

def _ler_digitado(request, subcategorias):
    return {s.id: request.POST.get(f"sub_{s.id}", "").strip() for s in subcategorias}


def _calcular_valores(subcategorias, digitado):
    try:
        return {
            s: (calcular(digitado[s.id]), digitado[s.id])
            for s in subcategorias if digitado[s.id]
        }
    except (ValueError, SyntaxError, InvalidOperation, ZeroDivisionError):
        raise ValueError("Há um valor inválido. Usa números e as operações + - * / (ex.: 50+20+100).")


def _guardar_valores(relatorio, subcategorias, valores, digitado):
    for s, (montante, expressao) in valores.items():
        Lancamento.objects.update_or_create(
            relatorio=relatorio, subcategoria=s,
            defaults={"montante": montante, "expressao": expressao},
        )
    vazias = [s for s in subcategorias if not digitado[s.id]]
    Lancamento.objects.filter(relatorio=relatorio, subcategoria__in=vazias).delete()


# ---------- Novo / editar / apagar ----------

def novo_relatorio(request):
    subcategorias = list(SubCategoria.objects.filter(ativa=True))
    grupos = _agrupar(subcategorias)
    existentes = [m.strftime("%Y-%m") for m in Relatorio.objects.values_list("mes", flat=True)]
    hoje = date.today()
    ano_sel, mes_sel = hoje.year, hoje.month
    digitado = {}
    erro = None

    if request.method == "POST":
        digitado = _ler_digitado(request, subcategorias)
        data = ler_mes(request)
        if data is None:
            erro = "Escolhe um mês e um ano válidos."
        else:
            ano_sel, mes_sel = data.year, data.month
            if Relatorio.objects.filter(mes=data).exists():
                erro = "Já existe um relatório para este mês. Vai à tabela e carrega em Editar."
            else:
                try:
                    valores = _calcular_valores(subcategorias, digitado)
                except ValueError as e:
                    erro = str(e)
                else:
                    with transaction.atomic():
                        relatorio = Relatorio.objects.create(mes=data)
                        _guardar_valores(relatorio, subcategorias, valores, digitado)
                    return redirect("relatorios:lista")

    for s in subcategorias:
        s.valor_atual = digitado.get(s.id, "")

    return render(request, "relatorios/novo.html", {
        "grupos": grupos,
        "erro": erro,
        "meses": MESES,
        "anos": anos_disponiveis(),
        "ano_sel": ano_sel,
        "mes_sel": mes_sel,
        "existentes": existentes,
    })


def editar_relatorio(request, pk):
    relatorio = get_object_or_404(Relatorio, pk=pk)
    subcategorias = list(SubCategoria.objects.filter(ativa=True))
    grupos = _agrupar(subcategorias)
    erro = None

    if request.method == "POST":
        digitado = _ler_digitado(request, subcategorias)
        try:
            valores = _calcular_valores(subcategorias, digitado)
        except ValueError as e:
            erro = str(e)
        else:
            with transaction.atomic():
                _guardar_valores(relatorio, subcategorias, valores, digitado)
            return redirect("relatorios:lista")
    else:
        atuais = Lancamento.objects.filter(relatorio=relatorio)
        digitado = {l.subcategoria_id: (l.expressao or str(l.montante)) for l in atuais}

    for s in subcategorias:
        s.valor_atual = digitado.get(s.id, "")

    return render(request, "relatorios/editar.html", {
        "relatorio": relatorio,
        "grupos": grupos,
        "erro": erro,
    })


@require_POST
def apagar_relatorio(request, pk):
    get_object_or_404(Relatorio, pk=pk).delete()
    return redirect("relatorios:lista")


def nova_subcategoria(request):
    form = SubCategoriaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("relatorios:novo")
    return render(request, "relatorios/subcategoria.html", {"form": form})