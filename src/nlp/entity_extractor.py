import re
from src.utils.text_cleaner import limpiar_texto
from src.utils.rules import PRODUCTOS, PATRONES_AREA, PATRON_CANTIDAD, PATRON_LOTE

def extraer_entidades(texto: str) -> dict:
    t = limpiar_texto(texto)
    entidades = {}

    for prod in PRODUCTOS:
        if prod in t:
            entidades["PRODUCTO"] = prod
            break

    for patron in PATRONES_AREA:
        m = re.search(patron, t)
        if m:
            entidades["AREA"] = m.group(0).strip()
            break

    m_cant = re.search(PATRON_CANTIDAD, t)
    if m_cant:
        entidades["CANTIDAD"] = m_cant.group(0).strip()

    m_lote = re.search(PATRON_LOTE, t)
    if m_lote:
        entidades["CODIGO_LOTE"] = m_lote.group(0).upper().strip()

    return entidades