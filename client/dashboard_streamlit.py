import time
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Monitor NLP Agroexportadora Ica", layout="wide")
st.title("Monitor Operativo NLP - Agroexportadora Ica")

with st.sidebar:
    st.header("Conexión LAN")
    server_ip = st.text_input("IP PC Servidor", value="127.0.0.1")
    base_url = f"http://{server_ip.strip()}:8001"
    auto_refresh = st.checkbox("Auto-actualizar (cada 3s)", value=True)

    if st.button("Reiniciar Estadísticas", type="primary"):
        try:
            requests.post(f"{base_url}/nlp/estadisticas/reiniciar", timeout=3)
            st.success("Estadísticas reiniciadas")
        except Exception as e:
            st.error(f"Error: {e}")

# Simulador de envío manual
st.subheader("Simulador de Mensajes Operativos")
col_in, col_btn = st.columns([4, 1])
with col_in:
    msg_manual = st.text_input("Escribe un reporte de campo, frío, empaque o despacho:",
                               placeholder="Ej: La camara de frio 2 subio a 9 grados con 120 cajas de uva red globe")
with col_btn:
    st.write("")
    st.write("")
    if st.button("Enviar Mensaje") and msg_manual.strip():
        try:
            r = requests.post(f"{base_url}/nlp/entender-comando", json={"texto": msg_manual}, timeout=4)
            st.json(r.json())
        except Exception as e:
            st.error(f"No se pudo conectar al servidor: {e}")

st.divider()

# Consumo de estadísticas
try:
    stats = requests.get(f"{base_url}/nlp/estadisticas", timeout=3).json()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Mensajes", stats["total_mensajes"])
    k2.metric("Confianza Promedio", f"{int(stats['confianza_promedio'] * 100)}%")
    k3.metric("Tasa de Derivación", f"{int(stats['tasa_derivacion'] * 100)}%")
    k4.metric("Alertas Críticas", stats["alertas_criticas"])

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Distribución por Intención")
        df_int = pd.DataFrame(list(stats["por_intencion"].items()), columns=["Intención", "Cantidad"]).set_index("Intención")
        st.bar_chart(df_int)
    with c2:
        st.subheader("Distribución por Sentimiento")
        df_sent = pd.DataFrame(list(stats["por_sentimiento"].items()), columns=["Sentimiento", "Cantidad"]).set_index("Sentimiento")
        st.bar_chart(df_sent)

    st.subheader("Bitácora Reciente en Tiempo Real")
    if stats["bitacora_reciente"]:
        df_hist = pd.DataFrame(stats["bitacora_reciente"])
        st.dataframe(df_hist, use_container_width=True)
    else:
        st.info("Aún no se han recibido mensajes en esta sesión.")

except Exception as e:
    st.warning(f"Esperando conexión con el servidor en {base_url}... ({e})")

if auto_refresh:
    time.sleep(3)
    st.rerun()