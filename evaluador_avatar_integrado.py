import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import tempfile
import json
import requests
import time


# --- Configuración Inicial y Carga de Datos ---
st.set_page_config(
    page_title="Evaluador Interactivo de Python",
    layout="wide" # Usamos el layout "wide" del Archivo 1 para más espacio
)

st.markdown("<h1 style='text-align: center; margin-bottom: 20px'>🎓 Evaluador Interactivo de Python con Asistente</h1>", unsafe_allow_html=True)

# Cargar preguntas
try:
    with open("preguntas.json", "r", encoding="utf-8") as f:
        preguntas = json.load(f)
except FileNotFoundError:
    st.error("Error: El archivo 'preguntas.json' no se encontró. Asegúrate de tenerlo en el mismo directorio.")
    st.stop() # Detiene la ejecución si el archivo no existe

# Inicializar resultados y estado de la pregunta actual
if "resultados" not in st.session_state:
    st.session_state.resultados = []
if "pregunta_idx" not in st.session_state:
    st.session_state.pregunta_idx = 0

# --- Funciones Auxiliares ---

# Función para reproducir texto como voz (utiliza gTTS y Streamlit.audio)
def reproducir_audio_st(texto, lang="es"):
    tts = gTTS(text=texto, lang=lang)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        st.audio(fp.name, format="audio/mp3", loop=False) # Reproducción con Streamlit

# Transcribir audio grabado (mejorada para usar directamente los bytes de Streamlit)
@st.cache_resource # Almacena en caché el inicializador del reconocedor
def get_recognizer():
    return sr.Recognizer()

def transcribir_audio_bytes(audio_bytes):
    r = get_recognizer()
    try:
        # Crea un archivo WAV temporal a partir de los bytes para SpeechRecognition
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_bytes)
            audio_path = temp_audio.name
        
        with sr.AudioFile(audio_path) as source:
            audio_data = r.record(source)
            texto = r.recognize_google(audio_data, language="es-ES")
            return texto
    except sr.UnknownValueError:
        return "[No se pudo entender el audio. Intenta hablar más claro.]"
    except sr.RequestError as e:
        return f"[Error del servicio de reconocimiento de voz: {e}. Revisa tu conexión a internet.]"
    finally:
        if 'audio_path' in locals() and tempfile.os.path.exists(audio_path):
            tempfile.os.remove(audio_path) # Limpia el archivo temporal

# Generar mensaje de evaluación
def generar_mensaje(nombre, puntaje, total):
    if puntaje / total >= 0.8:
        return f"¡Hola {nombre}! Felicidades, obtuviste {puntaje} de {total} en tu evaluación de Python. ¡Gran trabajo!"
    else:
        return f"Hola {nombre}, tu puntaje fue {puntaje} de {total}. Te animo a repasar algunos temas y volver a intentarlo. ¡Tú puedes!"

# Llamar a D-ID para generar avatar con video (opcional y sin cambios)
def generar_video_did(api_key, mensaje):
    if not api_key:
        return None
    url = "https://api.d-id.com/talks"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "script": {
            "type": "text",
            "input": mensaje,
            "provider": {"type": "google", "voice_id": "es-ES-Neural2-B"}
        },
        "source_url": "https://create-images-results.d-id.com/DefaultFriendlyTutor.png",
        "driver_url": "bank://lively",
        "config": {"fluent": True}
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        talk_id = response.json()['id']
        for _ in range(10): # Espera hasta 20 segundos
            check = requests.get(f"https://api.d-id.com/talks/{talk_id}", headers=headers)
            if check.status_code == 200 and check.json().get("status") == "done":
                return check.json().get("result_url")
            time.sleep(2)
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error al conectar con D-ID: {e}. Revisa tu API Key y conexión.")
        return None

# --- Interfaz Principal ---

# Información del usuario y API Key
st.sidebar.header("Configuración")
nombre = st.sidebar.text_input("Ingresa tu nombre:")
api_key = st.sidebar.text_input("API Key de D-ID (opcional):", type="password")

st.markdown("---")

# Título de la sección de la pregunta
st.markdown("<h3 style='text-align: center; margin-bottom: 0px'>¿Por qué es necesario preprocesar los datos que vamos a subir al modelo?</h1><br>", unsafe_allow_html=True)

# Diseño de 3 columnas (similar al Archivo 1)
col1, col2, col3 = st.columns([0.45, 0.1, 0.45]) # Ajusta las proporciones si es necesario

with col1:
    st.markdown('<br>' * 1, unsafe_allow_html=True)
    st.image("https://images.openai.com/thumbnails/bc4fd35a4319dcd1189035f5f2adbc1e.jpeg", width=200)
    st.write("**Tu Respuesta**")

    current_pregunta = preguntas[st.session_state.pregunta_idx]
    st.markdown(f"### Pregunta: {current_pregunta['pregunta']}")

    # Botón para escuchar la pregunta
    if st.button("🔊 Escuchar pregunta", key="listen_question"):
        reproducir_audio_st(current_pregunta["pregunta"])

    # Grabador de audio nativo (del Archivo 1)
    audio_grabado_bytes = st.audio_recorder("Presiona para grabar tu respuesta", key="audio_recorder_alumno")
    
    respuesta_transcrita = ""
    if audio_grabado_bytes:
        with st.spinner("Transcribiendo tu respuesta..."):
            respuesta_transcrita = transcribir_audio_bytes(audio_grabado_bytes)
        st.markdown("**Transcripción de tu respuesta:**")
        st.info(respuesta_transcrita)

        # Evaluación básica por coincidencia de palabras clave
        palabras_clave = current_pregunta.get("respuestas", [])
        puntaje = sum(1 for palabra in palabras_clave if palabra.lower() in respuesta_transcrita.lower())
        total = len(palabras_clave)
        st.success(f"Puntaje: {puntaje} de {total}")

        # Guardar resultado en el estado de la sesión
        st.session_state.resultados.append((current_pregunta['pregunta'], respuesta_transcrita, puntaje, total))

        if nombre:
            mensaje_evaluacion = generar_mensaje(nombre, puntaje, total)
            st.info(mensaje_evaluacion)

            if api_key:
                st.subheader("Asistente Virtual")
                with st.spinner("Generando avatar del asistente..."):
                    video_url = generar_video_did(api_key, mensaje_evaluacion)
                    if video_url:
                        st.video(video_url)
                    else:
                        st.warning("No se pudo generar el video del avatar. Revisa la API Key o intenta más tarde.")

with col3:
    st.image("https://cdn-icons-png.flaticon.com/512/1869/1869679.png", width=200)
    st.write("**Asistente (Profesor)**")
    # Audio pre-grabado (del Archivo 1 - asegúrate de tener 'response.mp3')
    try:
        audio_file = open("response.mp3", "rb")
        st.audio(audio_file.read(), format='audio/mp3', key="profesor_audio")
    except FileNotFoundError:
        st.warning("El archivo 'response.mp3' no se encontró. No se puede reproducir el audio del profesor.")

st.markdown("---")

# Botón para la siguiente pregunta
col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
with col_btn2:
    if st.button("**Próxima pregunta**", use_container_width=True):
        if st.session_state.pregunta_idx < len(preguntas) - 1:
            st.session_state.pregunta_idx += 1
            st.success("Siguiente pregunta cargada.")
            st.rerun() # Volver a cargar la página para mostrar la nueva pregunta
        else:
            st.info("¡Has completado todas las preguntas!")

# Mostrar historial de respuestas
st.markdown("---")
if st.checkbox("Mostrar historial de respuestas"):
    if st.session_state.resultados:
        st.subheader("Historial de Respuestas")
        for i, (preg, resp, punt, tot) in enumerate(st.session_state.resultados):
            st.markdown(f"**Pregunta {i+1}:** {preg}")
            st.markdown(f"**Tu Respuesta:** {resp}")
            st.markdown(f"**Puntaje:** {punt}/{tot}")
            st.markdown("---")
    else:
        st.info("Aún no has respondido ninguna pregunta.")