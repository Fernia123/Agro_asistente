import json
import os
import time
import requests
import streamlit as st

st.set_page_config(
    page_title="AgroIca NLP - Canal de Reportes",
    page_icon="🍇",
    layout="centered"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #0f172a 0%, #1e3a8a 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
    }
    .main-header h1 { margin: 0; font-size: 1.45rem; }
    .main-header p { margin: 4px 0 0 0; color: #cbd5e1; font-size: 0.88rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🍇 AgroIca — Envío de Reportes Operativos</h1>
    <p>Campo • Cámaras de Frío • Planta de Empaque • Despacho</p>
</div>
""", unsafe_allow_html=True)

# Inicializar historial del chat
if "chat_historial" not in st.session_state:
    st.session_state.chat_historial = [
        {
            "rol": "assistant",
            "tipo": "bienvenida",
            "texto": "Hola. Escribe aquí tu reporte operativo para enviarlo al sistema central."
        }
    ]

# Barra lateral mínima solo para configurar la IP del servidor LAN
with st.sidebar:
    st.header("🌐 Conexión Servidor")
    server_ip = st.text_input("IP PC Servidor", value="127.0.0.1", help="Ej: 192.168.137.1")
    base_url = f"http://{server_ip.strip()}:8001"

    st.divider()
    if st.button("🚀 Enviar Lote de Prueba (6)", use_container_width=True):
        ruta_json = os.path.join(os.path.dirname(__file__), "casos_prueba.json")
        if os.path.exists(ruta_json):
            with open(ruta_json, "r", encoding="utf-8") as f:
                casos = json.load(f)
            for c in casos:
                st.session_state.chat_historial.append({"rol": "user", "texto": c})
                try:
                    t0 = time.perf_counter()
                    r = requests.post(f"{base_url}/nlp/entender-comando", json={"texto": c}, timeout=5)
                    lat = (time.perf_counter() - t0) * 1000
                    r.raise_for_status()
                    st.session_state.chat_historial.append({
                        "rol": "assistant",
                        "tipo": "respuesta_nlp",
                        "data": r.json(),
                        "latencia": lat
                    })
                except Exception as e:
                    st.session_state.chat_historial.append({
                        "rol": "assistant",
                        "tipo": "error",
                        "texto": f"Error de conexión con `{base_url}`: {e}"
                    })
            st.rerun()
        else:
            st.warning("No se encontró `client/casos_prueba.json`.")

    if st.button("🧹 Limpiar Conversación", use_container_width=True):
        st.session_state.chat_historial = [st.session_state.chat_historial[0]]
        st.rerun()

def enviar_reporte(texto: str):
    st.session_state.chat_historial.append({"rol": "user", "texto": texto})
    try:
        t0 = time.perf_counter()
        r = requests.post(f"{base_url}/nlp/entender-comando", json={"texto": texto}, timeout=5)
        lat_ms = (time.perf_counter() - t0) * 1000
        r.raise_for_status()
        st.session_state.chat_historial.append({
            "rol": "assistant",
            "tipo": "respuesta_nlp",
            "data": r.json(),
            "latencia": lat_ms
        })
    except Exception as e:
        st.session_state.chat_historial.append({
            "rol": "assistant",
            "tipo": "error",
            "texto": f"No se pudo conectar con el servidor en `{base_url}` ({e})."
        })

# Mostrar mensajes del chat
for msg in st.session_state.chat_historial:
    with st.chat_message(msg["rol"], avatar="👷" if msg["rol"] == "user" else "🤖"):
        if msg["rol"] == "user":
            st.write(msg["texto"])
        else:
            if msg.get("tipo") in ("bienvenida", "error"):
                st.write(msg["texto"])
            else:
                res = msg["data"]
                lat = msg["latencia"]
                intencion = res["intencion"]
                conf_pct = int(res["confianza_intencion"] * 100)

                if intencion == "INTENCION_NO_CLARA":
                    st.warning(f"⚠️ **Reporte ambiguo ({conf_pct}%).** Derivado a supervisor.")
                else:
                    st.success(f"✅ **Reporte registrado y enrutado** ({lat:.0f} ms)")

                col1, col2, col3, col4 = st.columns(4)
                
                col4.markdown(f"**Acción**\n\n`{res['accion_sugerida']}`")

                if res["entidades"]:
                    ents = "  •  ".join([f"**{k}:** `{v}`" for k, v in res["entidades"].items()])
                    st.markdown(f"📌 **Entidades:** {ents}")

# Entrada fija inferior para escribir reportes
prompt = st.chat_input("Escribe tu reporte operativo aquí...")
if prompt and prompt.strip():
    enviar_reporte(prompt.strip())
    st.rerun()