import os
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from src.utils.text_cleaner import limpiar_texto

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

RUIDO_COMUN = [
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del",
    "al", "en", "con", "por", "para", "se", "su", "sus", "que", "y", "o",
    "a", "ante", "bajo", "como", "cuando", "donde", "esta", "este", "favor",
    "hola", "buenos", "dias", "tardes", "urgente", "porfa", "revisar"
]

def entrenar_sentimiento():
    csv_path = os.path.join(BASE_DIR, "train", "dataset_completo.csv")
    out_path = os.path.join(BASE_DIR, "models", "sentiment_pipeline.joblib")

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró el archivo en: {csv_path}. Revisa el nombre exacto en la carpeta train/")

    df = pd.read_csv(csv_path).dropna(subset=["texto", "sentimiento"])
    X = df["texto"].apply(limpiar_texto)
    y = df["sentimiento"].str.strip().str.upper()

    vectorizador = FeatureUnion([
        ("palabras", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words=RUIDO_COMUN)),
        ("caracteres", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True))
    ])

    pipeline = Pipeline([
        ("features", vectorizador),
        ("clf", LogisticRegression(max_iter=1500, C=10.0, class_weight="balanced"))
    ])
    pipeline.fit(X, y)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    joblib.dump(pipeline, out_path)
    print(f"[OK] Modelo de sentimiento guardado en {out_path} ({len(df)} registros)")

if __name__ == "__main__":
    entrenar_sentimiento()