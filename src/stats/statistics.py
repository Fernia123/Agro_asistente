from collections import Counter
from datetime import datetime

class StatsManager:
    def __init__(self):
        self.reset()

    def reset(self):
        self.total_mensajes = 0
        self.por_intencion = {
            "REPORTE_CALIDAD": 0,
            "FALLA_EQUIPO": 0,
            "CONSULTA_INVENTARIO": 0,
            "SOLICITUD_DESPACHO": 0,
            "INTENCION_NO_CLARA": 0
        }
        self.por_sentimiento = {"POSITIVO": 0, "NEUTRAL": 0, "NEGATIVO": 0}
        self.suma_confianza = 0.0
        self.derivados = 0
        self.alertas_criticas = 0
        self.entidades_counter = Counter()
        self.historial = []

    def registrar_evento(self, texto: str, intencion: str, confianza: float,
                         sentimiento: str, entidades: dict, accion: str):
        self.total_mensajes += 1
        self.por_intencion[intencion] = self.por_intencion.get(intencion, 0) + 1
        self.por_sentimiento[sentimiento] = self.por_sentimiento.get(sentimiento, 0) + 1
        self.suma_confianza += confianza

        if intencion == "INTENCION_NO_CLARA":
            self.derivados += 1
        if "ALERTA" in accion or "INMEDIATO" in accion:
            self.alertas_criticas += 1

        for tipo, val in entidades.items():
            self.entidades_counter[f"{tipo}: {val}"] += 1

        self.historial.insert(0, {
            "hora": datetime.now().strftime("%H:%M:%S"),
            "texto_original": texto,
            "intencion": intencion,
            "confianza_intencion": confianza,
            "sentimiento": sentimiento,
            "entidades": entidades,
            "accion_sugerida": accion
        })
        self.historial = self.historial[:25]

    def obtener_resumen(self) -> dict:
        conf_prom = round(self.suma_confianza / self.total_mensajes, 2) if self.total_mensajes > 0 else 0.0
        tasa_deriv = round(self.derivados / self.total_mensajes, 2) if self.total_mensajes > 0 else 0.0

        return {
            "total_mensajes": self.total_mensajes,
            "por_intencion": self.por_intencion,
            "por_sentimiento": self.por_sentimiento,
            "confianza_promedio": conf_prom,
            "tasa_derivacion": tasa_deriv,
            "alertas_criticas": self.alertas_criticas,
            "entidades_frecuentes": dict(self.entidades_counter.most_common(6)),
            "bitacora_reciente": self.historial
        }