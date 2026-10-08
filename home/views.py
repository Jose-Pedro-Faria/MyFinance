from collections import defaultdict
from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render

from dividas.models import Divida
from investimentos.models import Categoria as CategoriaInvestimento
from investimentos.models import Investimento
from patrimonio.models import Valor
from programadas.models import DespesaProgramada
from relatorios.models import Lancamento

ZERO = Decimal("0")


def _media(total, n):
    return total / n if n else None


def _indice(d):
    return d.year * 12 + d.month


def _f(x):
    return float(x) if x is not None else 0.0


def home(request):
    # ---------- Património (registos mensais) ----------
    pat = defaultdict(lambda: {"DIN": ZERO, "EME": ZERO, "INV": ZERO})
    linhas = (
        Valor.objects.values("registo__mes", "categoria__grupo")
        .annotate(t=Sum("montante"))
    )
    for r in linhas:
        pat[r["registo__mes"]][r["categoria__grupo"]] = r["t"]

    serie_pat = []
    for mes in sorted(pat):
        g = pat[mes]
        total = g["DIN"] + g["EME"] + g["INV"]
        serie_pat.append({
            "mes": mes, "din": g["DIN"], "eme": g["EME"], "inv": g["INV"],
            "total": total, "sem_eme": total - g["EME"],
        })
    ultimo = serie_pat[-1] if serie_pat else None
    anterior = serie_pat[-2] if len(serie_pat) > 1 else None
    variacao = ultimo["total"] - anterior["total"] if ultimo and anterior else None

    # ---------- Relatórios mensais ----------
    rel = defaultdict(lambda: {"REC": ZERO, "ESS": ZERO, "NES": ZERO})
    linhas = (
        Lancamento.objects.values("relatorio__mes", "subcategoria__tipo")
        .annotate(t=Sum("montante"))
    )
    for r in linhas:
        rel[r["relatorio__mes"]][r["subcategoria__tipo"]] = r["t"]

    serie_rel = []
    for mes in sorted(rel):
        g = rel[mes]
        serie_rel.append({
            "mes": mes, "rec": g["REC"], "ess": g["ESS"], "nes": g["NES"],
            "sobra": g["REC"] - g["ESS"] - g["NES"],
        })
    ultimo_rel = serie_rel[-1] if serie_rel else None

    n = len(serie_rel)
    media_rec = _media(sum((s["rec"] for s in serie_rel), ZERO), n)
    media_ess = _media(sum((s["ess"] for s in serie_rel), ZERO), n)
    media_nes = _media(sum((s["nes"] for s in serie_rel), ZERO), n)
    media_desp = _media(sum((s["ess"] + s["nes"] for s in serie_rel), ZERO), n)
    media_sobra = _media(sum((s["sobra"] for s in serie_rel), ZERO), n)

    # Totais por ano e médias anuais
    por_ano = defaultdict(lambda: {"rec": ZERO, "desp": ZERO, "meses": 0})
    for s in serie_rel:
        a = por_ano[s["mes"].year]
        a["rec"] += s["rec"]
        a["desp"] += s["ess"] + s["nes"]
        a["meses"] += 1
    tabela_anos = [
        {"ano": ano, "meses": a["meses"], "rec": a["rec"], "desp": a["desp"],
         "sobra": a["rec"] - a["desp"]}
        for ano, a in sorted(por_ano.items())
    ]
    na = len(tabela_anos)
    media_anual_rec = _media(sum((a["rec"] for a in tabela_anos), ZERO), na)
    media_anual_desp = _media(sum((a["desp"] for a in tabela_anos), ZERO), na)
    media_anual_sobra = _media(sum((a["sobra"] for a in tabela_anos), ZERO), na)

    # ---------- Investimentos (valores atuais) ----------
    investimentos = list(Investimento.objects.all())
    inv_por_cat = [
        {
            "nome": nome,
            "total": sum((i.valor_total for i in investimentos if i.categoria == cod), ZERO),
        }
        for cod, nome in CategoriaInvestimento.choices
    ]
    inv_total = sum((c["total"] for c in inv_por_cat), ZERO)

    # ---------- Dívidas ----------
    ativas = [d for d in Divida.objects.all() if d.meses_em_falta > 0]
    mensalidade_total = sum((d.mensalidade for d in ativas), ZERO)
    divida_total = sum((d.total_em_falta for d in ativas), ZERO)

    # ---------- Despesas programadas pendentes ----------
    pendentes = list(
        DespesaProgramada.objects.filter(paga=False)
        .annotate(m=TruncMonth("data")).values("m")
        .annotate(t=Sum("valor")).order_by("m")
    )
    pendentes_total = sum((p["t"] for p in pendentes), ZERO)

    # ---------- Cruzamentos ----------
    patrimonio_liquido = ultimo["total"] - divida_total if ultimo else None
    taxa_esforco = mensalidade_total / media_rec * 100 if media_rec else None
    meses_emergencia = ultimo["eme"] / media_ess if ultimo and media_ess else None
    cobertura_pendentes = (
        pendentes_total / media_sobra if media_sobra and media_sobra > 0 else None
    )

    # Sobra do mês vs variação do património (só meses consecutivos)
    sobra_por_mes = {s["mes"]: s["sobra"] for s in serie_rel}
    comparacao = []
    for i in range(1, len(serie_pat)):
        atual, ant = serie_pat[i], serie_pat[i - 1]
        if _indice(atual["mes"]) - _indice(ant["mes"]) != 1:
            continue
        if atual["mes"] not in sobra_por_mes:
            continue
        var = atual["total"] - ant["total"]
        sobra = sobra_por_mes[atual["mes"]]
        comparacao.append({
            "mes": atual["mes"], "sobra": sobra,
            "variacao": var, "diferenca": var - sobra,
        })
    comparacao = comparacao[-12:][::-1]

    # ---------- Dados para os gráficos ----------
    dados = {
        "patrimonio": {
            "meses": [s["mes"].strftime("%m/%Y") for s in serie_pat],
            "total": [_f(s["total"]) for s in serie_pat],
            "sem_eme": [_f(s["sem_eme"]) for s in serie_pat],
            "din": [_f(s["din"]) for s in serie_pat],
            "eme": [_f(s["eme"]) for s in serie_pat],
            "inv": [_f(s["inv"]) for s in serie_pat],
        },
        "fluxo": {
            "meses": [s["mes"].strftime("%m/%Y") for s in serie_rel],
            "rec": [_f(s["rec"]) for s in serie_rel],
            "ess": [_f(s["ess"]) for s in serie_rel],
            "nes": [_f(s["nes"]) for s in serie_rel],
            "sobra": [_f(s["sobra"]) for s in serie_rel],
        },
        "investimentos": {
            "nomes": [c["nome"] for c in inv_por_cat],
            "valores": [_f(c["total"]) for c in inv_por_cat],
        },
    }

    return render(request, "home/home.html", {
        "ultimo": ultimo, "anterior": anterior, "variacao": variacao,
        "ultimo_rel": ultimo_rel,
        "media_rec": media_rec, "media_ess": media_ess, "media_nes": media_nes,
        "media_desp": media_desp, "media_sobra": media_sobra,
        "tabela_anos": tabela_anos,
        "media_anual_rec": media_anual_rec, "media_anual_desp": media_anual_desp,
        "media_anual_sobra": media_anual_sobra,
        "inv_total": inv_total,
        "mensalidade_total": mensalidade_total, "divida_total": divida_total,
        "pendentes": pendentes, "pendentes_total": pendentes_total,
        "patrimonio_liquido": patrimonio_liquido, "taxa_esforco": taxa_esforco,
        "meses_emergencia": meses_emergencia,
        "cobertura_pendentes": cobertura_pendentes,
        "comparacao": comparacao,
        "dados": dados,
    })