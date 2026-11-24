import os
import time
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="AgroIca NLP Cloud", page_icon="🍇", layout="wide")

# URL del backend configurada por variable de entorno o secreto de Streamlit Cloud
try:
    API_URL = st.secrets["API_URL"]
except Exception:
    API_URL = os.getenv("API_URL", "https://agro-asistente.onrender.com")

if "sesion" not in st.session_state:
    st.session_state.sesion = None
if "chat_historial" not in st.session_state:
    st.session_state.chat_historial = []

# ==============================================================================
# PANTALLA DE INICIO DE SESIÓN (SI NO ESTÁ AUTENTICADO)
# ==============================================================================
if st.session_state.sesion is None:
    col_izq, col_centro, col_der = st.columns([1, 1.4, 1])
    with col_centro:
        st.markdown("## 🍇 AgroIca NLP — Acceso Remoto")
        st.caption("Sistema de Comprensión de Lenguaje Operativo en la Nube")
        with st.form("form_login"):
            user = st.text_input("Usuario")
            pwd = st.text_input("Contraseña", type="password")
            btn = st.form_submit_button("Iniciar Sesión", type="primary", use_container_width=True)

        if btn:
            try:
                r = requests.post(f"{API_URL}/auth/login", json={"username": user.strip(), "password": pwd}, timeout=8)
                if r.status_code == 200:
                    st.session_state.sesion = r.json()
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos (401 Unauthorized).")
            except Exception as e:
                st.error(f"Error de conexión con el servidor cloud: {e}")
    st.stop()

# ==============================================================================
# SESIÓN ACTIVA: CABECERA CON ROL Y BOTÓN CERRAR SESIÓN
# ==============================================================================
sesion = st.session_state.sesion
headers = {"Authorization": f"Bearer {sesion['access_token']}"}
rol = sesion["rol"]

c_head1, c_head2 = st.columns([4, 1])
with c_head1:
    st.markdown(f"### 🍇 AgroIca NLP — {sesion['nombre']} (`ROL: {rol}`)")
with c_head2:
    if st.button("Cerrar Sesión", use_container_width=True):
        st.session_state.sesion = None
        st.session_state.chat_historial = []
        st.rerun()

st.divider()

# ==============================================================================
# INTERFAZ EXCLUSIVA PARA ROL: OPERADOR (SOLO CHAT DE REPORTES)
# ==============================================================================
if rol == "OPERADOR":
    st.info("Canal operativo habilitado. Envía tus reportes de campo, frío, packing o despacho.")

    for msg in st.session_state.chat_historial:
        with st.chat_message(msg["rol"], avatar="👷" if msg["rol"] == "user" else "🤖"):
            if msg["rol"] == "user":
                st.write(msg["texto"])
            else:
                res = msg["data"]
                st.success(f"Reporte procesado — Intención: `{res['intencion']}` ({int(res['confianza_intencion']*100)}%)")
                st.write(f"**Sentimiento:** `{res['sentimiento']}` | **Acción:** `{res['accion_sugerida']}`")
                if res.get("entidades"):
                    st.caption(f"Entidades: {res['entidades']}")

    prompt = st.chat_input("Escribe tu reporte operativo...")
    if prompt and prompt.strip():
        st.session_state.chat_historial.append({"rol": "user", "texto": prompt.strip()})
        r = requests.post(f"{API_URL}/nlp/entender-comando", json={"texto": prompt.strip()}, headers=headers, timeout=8)
        if r.status_code == 200:
            st.session_state.chat_historial.append({"rol": "assistant", "data": r.json()})
            st.rerun()
        elif r.status_code == 401:
            st.error("Tu sesión expiró (401). Vuelve a iniciar sesión.")
            st.session_state.sesion = None

# ==============================================================================
# INTERFAZ EXCLUSIVA PARA ROL: SUPERVISOR (DASHBOARD + ESTADÍSTICAS + PRUEBAS)
# ==============================================================================
elif rol == "SUPERVISOR":
    tab_dash, tab_test = st.tabs(["📊 Dashboard y Estadísticas en Vivo", "🧪 Simulador de Análisis"])

    with tab_dash:
        col_top1, col_top2 = st.columns([3.5, 1])
        with col_top1:
            st.subheader("Monitoreo Global de Operaciones")
        with col_top2:
            if st.button("🗑️ Reiniciar Estadísticas", use_container_width=True):
                requests.post(f"{API_URL}/nlp/estadisticas/reiniciar", headers=headers, timeout=5)
                st.rerun()

        r_stats = requests.get(f"{API_URL}/nlp/estadisticas", headers=headers, timeout=6)
        if r_stats.status_code != 200:
            st.error(f"Error al obtener estadísticas ({r_stats.status_code}).")
            st.stop()

        stats = r_stats.json()
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Mensajes", stats["total_mensajes"])
        k2.metric("Confianza Promedio", f"{int(stats['confianza_promedio']*100)}%")
        k3.metric("Tasa de Derivación", f"{int(stats['tasa_derivacion']*100)}%")
        k4.metric("Alertas Críticas", stats["alertas_criticas"])

        g1, g2 = st.columns(2)
        with g1:
            st.bar_chart(pd.DataFrame(list(stats["por_intencion"].items()), columns=["Intención", "Total"]).set_index("Intención"))
        with g2:
            st.bar_chart(pd.DataFrame(list(stats["por_sentimiento"].items()), columns=["Sentimiento", "Total"]).set_index("Sentimiento"))

        st.subheader("Bitácora Reciente de Reportes")
        if stats["bitacora_reciente"]:
            df_bit = pd.DataFrame(stats["bitacora_reciente"])
            st.dataframe(df_bit, use_container_width=True, hide_index=True)
            st.download_button(
                "📥 Descargar Bitácora CSV",
                data=df_bit.to_csv(index=False).encode("utf-8"),
                file_name="reportes_agroica_cloud.csv",
                mime="text/csv"
            )
        else:
            st.info("Sin reportes registrados todavía.")

    with tab_test:
        txt_sup = st.text_input("Probar consulta directa como Supervisor:")
        if st.button("Analizar Mensaje") and txt_sup.strip():
            r_test = requests.post(f"{API_URL}/nlp/entender-comando", json={"texto": txt_sup.strip()}, headers=headers, timeout=6)
            st.json(r_test.json())
