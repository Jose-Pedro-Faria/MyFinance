import ast
import re
from decimal import Decimal

CARACTERES_VALIDOS = re.compile(r"^[0-9.+\-*/() ]+$")


def calcular(texto):
    """Calcula expressões como '50+20+100' e devolve um Decimal com 2 casas."""
    texto = texto.replace(",", ".").replace("€", "").strip()
    if not texto or len(texto) > 200 or not CARACTERES_VALIDOS.match(texto):
        raise ValueError("Expressão inválida")
    arvore = ast.parse(texto, mode="eval")
    return _avaliar(arvore.body, texto).quantize(Decimal("0.01"))


def _avaliar(no, texto):
    if isinstance(no, ast.Constant) and isinstance(no.value, (int, float)):
        return Decimal(ast.get_source_segment(texto, no))
    if isinstance(no, ast.UnaryOp) and isinstance(no.op, (ast.UAdd, ast.USub)):
        valor = _avaliar(no.operand, texto)
        return -valor if isinstance(no.op, ast.USub) else valor
    if isinstance(no, ast.BinOp):
        esq = _avaliar(no.left, texto)
        dir_ = _avaliar(no.right, texto)
        if isinstance(no.op, ast.Add):
            return esq + dir_
        if isinstance(no.op, ast.Sub):
            return esq - dir_
        if isinstance(no.op, ast.Mult):
            return esq * dir_
        if isinstance(no.op, ast.Div):
            return esq / dir_
    raise ValueError("Expressão inválida")