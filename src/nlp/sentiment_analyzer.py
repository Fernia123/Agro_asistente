import joblib
from src.utils.text_cleaner import limpiar_texto
from src.utils.rules import extraer_terminos_clave

class SentimentAnalyzer:
    def __init__(self, model_path="models/sentiment_pipeline.joblib"):
        self.pipeline = joblib.load(model_path)

    def analyze(self, texto: str) -> dict:
        t_limpio = limpiar_texto(texto)
        probas = self.pipeline.predict_proba([t_limpio])[0]
        idx_max = probas.argmax()
        confianza = round(float(probas[idx_max]), 2)
        sentimiento = str(self.pipeline.classes_[idx_max])
        terminos = extraer_terminos_clave(t_limpio)

        return {
            "sentimiento": sentimiento,
            "confianza": confianza,
            "terminos_clave": terminos
        }