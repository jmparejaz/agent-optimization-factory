# ⚙️ Config - Configuración del Agente
# Este módulo centraliza la configuración del agente de WhatsApp.

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# --- Configuración de Twilio ---
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# --- Configuración de Firestore ---
FIRESTORE_COLLECTION_KNOWLEDGE = os.getenv("FIRESTORE_COLLECTION_KNOWLEDGE", "knowledge_base")
FIRESTORE_COLLECTION_PRODUCTS = os.getenv("FIRESTORE_COLLECTION_PRODUCTS", "products")
FIRESTORE_COLLECTION_FAQ = os.getenv("FIRESTORE_COLLECTION_FAQ", "faq")
FIRESTORE_COLLECTION_SESSIONS = os.getenv("FIRESTORE_COLLECTION_SESSIONS", "chat_sessions")

# --- Configuración del LLM ---
# Opciones: "mistral-tiny", "mistral-small", "openrouter:mistralai/mistral-tiny", "gemini-1.0-pro"
LLM_MODEL = os.getenv("LLM_MODEL", "mistral-tiny")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Configuración de Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# --- Configuración de Cloud Run ---
SERVICE_NAME = os.getenv("SERVICE_NAME", "whatsapp-agent-backend")
REGION = os.getenv("REGION", "us-central1")

# --- Validación de configuración ---
def validate_config():
    """
    Valida que las variables de entorno obligatorias estén configuradas.
    
    Raises:
        ValueError: Si falta alguna variable obligatoria.
    """
    required_vars = {
        "TWILIO_ACCOUNT_SID": TWILIO_ACCOUNT_SID,
        "TWILIO_AUTH_TOKEN": TWILIO_AUTH_TOKEN
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        raise ValueError(
            f"Faltan variables de entorno obligatorias: {', '.join(missing_vars)}. "
            "Configúralas en el archivo .env o en las variables de entorno."
        )
    
    # Validar que al menos una API key de LLM esté configurada
    llm_keys = [MISTRAL_API_KEY, OPENROUTER_API_KEY, GEMINI_API_KEY]
    if not any(llm_keys):
        raise ValueError(
            "No se encontró ninguna API key de LLM. "
            "Configura al menos una de: MISTRAL_API_KEY, OPENROUTER_API_KEY, GEMINI_API_KEY."
        )


# Validar configuración al importar el módulo
try:
    validate_config()
except ValueError as e:
    print(f"⚠️  Advertencia: {e}")
