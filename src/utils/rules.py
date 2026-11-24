import re

PRODUCTOS = [
    "uva red globe", "red globe", "uva sweet globe", "sweet globe",
    "uva crimson", "crimson", "uva autumn crisp", "esparrago verde",
    "esparrago blanco", "esparrago", "uva", "clamshell", "jabas", "pallets"
]

PATRONES_AREA = [
    r"camara de frio\s*\d*", r"camara\s*\d*", r"tunel de enfriamiento\s*\d*",
    r"linea de empaque\s*\d*", r"linea\s*\d*", r"packing",
    r"campo\s*[a-z0-9]*", r"fundo\s*[a-z0-9]*", r"muelle de carga",
    r"muelle\s*\d*", r"almacen\s*[a-z0-9]*", r"zona de despacho"
]

PATRON_CANTIDAD = r"\b\d+(?:[.,]\d+)?\s*(?:cajas|pallets|jabas|kg|kilos|toneladas|grados|°c|unidades)\b"
PATRON_LOTE = r"\b(?:lote|lt|l)[\s\-_]*\d+[a-z0-9]*\b"

STOPWORDS_ES = {
    "para", "como", "pero", "esta", "este", "con", "los", "las", "del",
    "una", "uno", "unos", "unas", "por", "que", "sin", "sobre", "entre",
    "desde", "hasta", "donde", "cuando", "favor", "urgente", "hola"
}

def extraer_terminos_clave(texto_limpio: str, top_n: int = 5) -> list[str]:
    tokens = re.findall(r"\b[a-z]{4,}\b", texto_limpio)
    claves = []
    for t in tokens:
        if t not in STOPWORDS_ES and t not in claves:
            claves.append(t)
    return claves[:top_n]