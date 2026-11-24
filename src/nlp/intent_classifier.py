import re
import joblib
from src.utils.text_cleaner import limpiar_texto

class IntentClassifier:
    def __init__(self, model_path="models/intent_pipeline.joblib", threshold=0.65):
        self.pipeline = joblib.load(model_path)
        self.threshold = threshold

    def predict(self, texto: str) -> tuple[str, float]:
        t_limpio = limpiar_texto(texto)
        tokens = re.findall(r"\b[a-z0-9]{2,}\b", t_limpio)

        # Solo bloquear textos vacíos o ruido puro de 1 palabra (ej. "hola", "asdf")
        if len(tokens) < 2:
            return "INTENCION_NO_CLARA", 0.30

        probas = self.pipeline.predict_proba([t_limpio])[0]
        idx_max = probas.argmax()
        confianza = round(float(probas[idx_max]), 2)
        intencion = str(self.pipeline.classes_[idx_max])

        if confianza < self.threshold:
            return "INTENCION_NO_CLARA", confianza

        return intencion, confianza