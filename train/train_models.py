import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

# ============================================
# 1. Cargar el dataset
# ============================================
df = pd.read_csv("dataset_completo.csv")

print("Distribución de intenciones:")
print(df["intencion"].value_counts())
print("\nDistribución de sentimientos:")
print(df["sentimiento"].value_counts())
print("-" * 50)

# ============================================
# 2. Entrenar modelo de INTENCIONES
# ============================================
print("\n Entrenando modelo de INTENCIONES...")

X = df["texto"]
y_intent = df["intencion"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y_intent, test_size=0.2, random_state=42, stratify=y_intent
)

intent_pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        analyzer="word",
        sublinear_tf=True
    )),
    ("clf", LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        C=2.0,
        random_state=42
    ))
])

intent_pipeline.fit(X_train, y_train)

# Evaluación
y_pred = intent_pipeline.predict(X_test)
print("\n--- Resultados INTENCIONES ---")
print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
print(classification_report(y_test, y_pred))

# ============================================
# 3. Entrenar modelo de SENTIMIENTO
# ============================================
print("\n Entrenando modelo de SENTIMIENTO...")

y_sent = df["sentimiento"]

X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(
    X, y_sent, test_size=0.2, random_state=42, stratify=y_sent
)

sentiment_pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        analyzer="word",
        sublinear_tf=True
    )),
    ("clf", LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        C=2.0,
        random_state=42
    ))
])

sentiment_pipeline.fit(X_train_s, y_train_s)

# Evaluación
y_pred_s = sentiment_pipeline.predict(X_test_s)
print("\n--- Resultados SENTIMIENTO ---")
print(f"Accuracy: {accuracy_score(y_test_s, y_pred_s):.3f}")
print(classification_report(y_test_s, y_pred_s))

# ============================================
# 4. Guardar los modelos entrenados
# ============================================
os.makedirs("models", exist_ok=True)

joblib.dump(intent_pipeline, "models/intent_pipeline.joblib")
joblib.dump(sentiment_pipeline, "models/sentiment_pipeline.joblib")

print("\n Modelos guardados correctamente en la carpeta /models")
print("   - models/intent_pipeline.joblib")
print("   - models/sentiment_pipeline.joblib")