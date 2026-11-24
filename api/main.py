import os
import sys

# Asegurar que se puedan importar los paquetes de src/ y api/ desde cualquier directorio
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.auth import autenticar_usuario, obtener_usuario_actual, requerir_supervisor
from src.nlp.intent_classifier import IntentClassifier
from src.nlp.sentiment_analyzer import SentimentAnalyzer
from src.nlp.entity_extractor import extraer_entidades
from src.nlp.action_suggester import sugerir_accion
from src.stats.statistics import StatsManager

app = FastAPI(title="API NLP Agroexportadora Ica (Cloud & Roles)", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar modelos entrenados con rutas absolutas (evita errores de directorio en Render/Cloud)
intent_clf = IntentClassifier(
    model_path=os.path.join(BASE_DIR, "models", "intent_pipeline.joblib"),
    threshold=0.65
)
sentiment_clf = SentimentAnalyzer(
    model_path=os.path.join(BASE_DIR, "models", "sentiment_pipeline.joblib")
)
stats = StatsManager()

class LoginRequest(BaseModel):
    username: str
    password: str

class TextoRequest(BaseModel):
    texto: str

@app.get("/")
def health_check():
    return {"estado": "activo", "servicio": "API NLP Agroexportadora Ica"}

# ==============================================================================
# AUTENTICACIÓN (Generación de Token JWT con Rol)
# ==============================================================================
@app.post("/auth/login")
def login(datos: LoginRequest):
    sesion = autenticar_usuario(datos.username, datos.password)
    if not sesion:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")
    return sesion

# ==============================================================================
# ENDPOINTS OPERATIVOS (Requieren Login: OPERADOR o SUPERVISOR -> sin token = 401)
# ==============================================================================
@app.post("/nlp/analizar-texto")
def analizar_texto(req: TextoRequest, usuario: dict = Depends(obtener_usuario_actual)):
    res_sent = sentiment_clf.analyze(req.texto)
    return {
        "texto_original": req.texto,
        "sentimiento": res_sent["sentimiento"],
        "confianza": res_sent["confianza"],
        "terminos_clave": res_sent["terminos_clave"]
    }

@app.post("/nlp/entender-comando")
def entender_comando(req: TextoRequest, usuario: dict = Depends(obtener_usuario_actual)):
    intencion, conf_intencion = intent_clf.predict(req.texto)
    res_sent = sentiment_clf.analyze(req.texto)
    sentimiento = res_sent["sentimiento"]
    entidades = extraer_entidades(req.texto)
    accion = sugerir_accion(intencion, sentimiento)

    stats.registrar_evento(
        texto=req.texto,
        intencion=intencion,
        confianza=conf_intencion,
        sentimiento=sentimiento,
        entidades=entidades,
        accion=accion
    )

    return {
        "texto_original": req.texto,
        "intencion": intencion,
        "confianza_intencion": conf_intencion,
        "sentimiento": sentimiento,
        "entidades": entidades,
        "accion_sugerida": accion,
        "reportado_por": usuario.get("sub")
    }

# ==============================================================================
# ENDPOINTS DE SUPERVISIÓN (Exclusivos SUPERVISOR -> sin token = 401, OPERADOR = 403)
# ==============================================================================
@app.get("/nlp/estadisticas")
def obtener_estadisticas(usuario: dict = Depends(requerir_supervisor)):
    return stats.obtener_resumen()

@app.post("/nlp/estadisticas/reiniciar")
def reiniciar_estadisticas(usuario: dict = Depends(requerir_supervisor)):
    stats.reset()
    return {"mensaje": "Estadísticas reiniciadas correctamente."}

if __name__ == "__main__":
    puerto = int(os.getenv("PORT", 8001))
    uvicorn.run("api.main:app", host="0.0.0.0", port=puerto, reload=False)