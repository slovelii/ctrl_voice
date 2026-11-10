import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import time
import paho.mqtt.client as paho
import json
import platform

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE LA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Supermarket Multi-Control — Automatización de Tienda",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# ESTILOS CSS: TEMÁTICA SUPERMERCADO (BLANCO, AZUL Y ROJO)
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif !important;
    }

    /* Fondo principal limpio y comercial */
    .stApp {
        background-color: #f8fafc !important;
    }

    /* Barra lateral estilo central de operaciones */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 2px solid #e2e8f0;
    }

    /* Tarjetas estilo góndola / estante de supermercado */
    .market-card {
        background: #ffffff !important;
        border: 2px solid #e2e8f0;
        border-top: 5px solid #2563eb; /* Acento Azul */
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }

    .voice-card {
        background: #eff6ff !important;
        border: 2px solid #bfdbfe;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        text-align: center;
    }

    /* Títulos institucionales */
    h1, h2, h3 {
        color: #1e3a8a !important;
        font-weight: 700 !important;
    }

    /* Botones corporativos en Azul con letras BLANCAS */
    .stButton button {
        background-color: #2563eb !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 20px;
        transition: all 0.2s ease;
    }

    .stButton button span {
        color: #ffffff !important;
    }

    .stButton button:hover {
        background-color: #1d4ed8 !important;
        transform: translateY(-1px);
    }

    p, span, label {
        color: #334155 !important;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONFIGURACIÓN MQTT
# ─────────────────────────────────────────────
broker = "broker.mqttdashboard.com"
port = 1883

def on_publish(client, userdata, result):
    print("El dato ha sido publicado con éxito \n")

def enviar_comando_mqtt(topic, payload_dict):
    """Función unificada para conectar y publicar comandos MQTT"""
    try:
        client = paho.Client("SUPERMARKET_MULTIMODAL_CLIENT")
        client.on_publish = on_publish
        client.connect(broker, port)
        message = json.dumps(payload_dict)
        client.publish(topic, message)
        client.disconnect()
        return True
    except Exception as e:
        st.error(f"Error de conexión MQTT: {e}")
        return False

# ─────────────────────────────────────────────
# BARRA LATERAL: CONFIGURACIÓN Y ESTADO
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛒 Centro de Control Comercial")
    st.markdown("Administra los accesos y la iluminación de los pasillos de frutas y verduras de forma manual o por comandos de voz.")
    st.divider()
    st.markdown(f"💻 **Python:** {platform.python_version()}")
    st.markdown(f"🌐 **Broker MQTT:** `{broker}`")
    st.markdown("🔴 **Estado:** Sistema Activo")

# ─────────────────────────────────────────────
# ENCABEZADO PRINCIPAL
# ─────────────────────────────────────────────
st.markdown("""
<div class="market-card" style="text-align: center;">
    <span style="background-color: #fee2e2; color: #dc2626; font-weight: 700; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;">🍎 SECCIÓN: FRUTAS & VERDURAS 🥦</span>
    <h1 style="margin: 10px 0 5px 0;">Automatización Multimodal de Tienda</h1>
    <p style="color: #64748b; font-size: 0.95rem; margin: 0;">
        Controla las 4 funciones principales del supermercado: Apertura/Cierre de puertas e iluminación general mediante voz o botones táctiles.
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SECCIÓN 1: CONTROL MULTIMODAL POR VOZ
# ─────────────────────────────────────────────
st.markdown("""
<div class="voice-card">
    <h3 style="color: #1e40af !important; margin-top: 0;">🎙️ Interfaz de Comandos por Voz</h3>
    <p style="margin-bottom: 15px;">Toca el botón de inicio y di claramente comandos como: <i>"abrir puerta", "cerrar puerta", "prender luces" o "apagar luces"</i>.</p>
</div>
""", unsafe_allow_html=True)

col_v1, col_v2, col_v3 = st.columns([1, 2, 1])
with col_v2:
    stt_button = Button(label="🎙️ Iniciar Escucha por Voz", width=250)

    stt_button.js_on_event("button_click", CustomJS(code="""
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'es-ES';
     
        recognition.onresult = function (e) {
            var value = e.results[0][0].transcript;
            if (value != "") {
                document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
            }
        }
        recognition.start();
        """))

    result = streamlit_bokeh_events(
        stt_button,
        events="GET_TEXT",
        key="listen_voice",
        refresh_on_update=False,
        override_height=75,
        debounce_time=0)

    if result and "GET_TEXT" in result:
        texto_reconocido = result.get("GET_TEXT").strip().lower()
        st.success(f"🗣️ Comando de voz detectado: **\"{texto_reconocido}\"**")
        
        # Publicar comando reconocido por voz al tópico MQTT
        exito = enviar_comando_mqtt("voice_ctrl", {"VoiceCommand": texto_reconocido})
        if exito:
            st.info(f"📡 Comando enviado al broker correctamente.")

st.divider()

# ─────────────────────────────────────────────
# SECCIÓN 2: CONTROL MANUAL DIRECTO (4 ORDENES ESPECÍFICAS)
# ─────────────────────────────────────────────
st.markdown("### 🎛️ Panel de Control Manual (4 Órdenes Clave)")

col_b1, col_b2 = st.columns(2)

with col_b1:
    st.markdown("#### 🚪 Control de Puertas")
    if st.button('🟢 ABRIR PUERTA', use_container_width=True):
        enviar_comando_mqtt("cmqtt_s", {"Door": "OPEN"})
        st.success("🚪 ¡Señal enviada: Puerta ABIERTA!")
        
    if st.button('🔴 CERRAR PUERTA', use_container_width=True):
        enviar_comando_mqtt("cmqtt_s", {"Door": "CLOSE"})
        st.warning("🚪 ¡Señal enviada: Puerta CERRADA!")

with col_b2:
    st.markdown("#### 💡 Control de Luces")
    if st.button('💡 PRENDER LUCES', use_container_width=True):
        enviar_comando_mqtt("cmqtt_s", {"Lights": "ON"})
        st.success("✨ ¡Señal enviada: Luces ENCENDIDAS!")
        
    if st.button('🌙 APAGAR LUCES', use_container_width=True):
        enviar_comando_mqtt("cmqtt_s", {"Lights": "OFF"})
        st.warning("🌙 ¡Señal enviada: Luces APAGADAS!")

st.divider()

# ─────────────────────────────────────────────
# RECOMENDACIONES DE OPERACIÓN EN LA TIENDA
# ─────────────────────────────────────────────
st.markdown("""
<div style="background-color: #eff6ff; border: 1px solid #bfdbfe; border-left: 5px solid #2563eb; border-radius: 10px; padding: 16px;">
    <h4 style="color: #1e40af !important; margin-top: 0;">💡 Guía Rápida para el Dueño del Supermercado</h4>
    <ul style="margin-bottom: 0; padding-left: 20px; color: #1e293b;">
        <li><b>Apertura de Puerta:</b> Actívelo al iniciar el horario comercial (08:00 hrs) para permitir el ingreso de clientes a la sección fresca.</li>
        <li><b>Cierre de Puerta:</b> Úselo al finalizar la jornada o para mantener climatización controlada en pasillos refrigerados.</li>
        <li><b>Prender/Apagar Luces:</b> Permite gestionar el brillo de las góndolas de frutas y verduras para realzar sus colores naturales o ahorrar energía.</li>
    </ul>
</div>
""", unsafe_allow_html=True)
