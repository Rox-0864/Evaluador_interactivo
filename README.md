# Evaluador Avatar Interactivo en Python

Este proyecto es una aplicación web construida con Streamlit que permite evaluar a estudiantes de Python a través de preguntas habladas. Utiliza reconocimiento de voz, síntesis de texto a voz y puede generar un avatar animado con la API de D-ID.

## Archivos incluidos

- `evaluador_avatar_integrado.py`: Código principal de la aplicación.
- `preguntas.json`: Archivo JSON con preguntas y palabras clave para evaluar.
- `requirements.txt`: Lista de dependencias necesarias.
- `README.md`: Esta guía de uso.

## Requisitos

- Python 3.8 o superior
- Dependencias: ver `requirements.txt`

## Instalación

1. Crea un entorno virtual (opcional pero recomendado):

   ```bash
   python -m venv venv
   source venv/bin/activate  # en Windows usa: venv\Scripts\activate
   ```

2. Instala los requisitos:

   ```bash
   pip install -r requirements.txt
   ```

## Ejecución

1. Ejecuta la app con:

   ```bash
   streamlit run evaluador_avatar_integrado.py
   ```

2. Abre el navegador en `http://localhost:8501`

## API D-ID (Opcional)

Si deseas que el avatar hable, puedes obtener una API Key gratuita en [https://www.d-id.com](https://www.d-id.com) y pegarla en el campo correspondiente de la app.

## Créditos

Creado como prototipo educativo para evaluación oral de estudiantes de Python.
# Evaluador_interactivo
