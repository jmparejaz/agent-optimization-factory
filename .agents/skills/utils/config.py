# ⚙️ Config - Configuración del Agente (cargada desde config.yaml)
# Este módulo centraliza la configuración del agente de WhatsApp.

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (opcional, para compatibilidad)
load_dotenv()

# Cargar configuración desde config.yaml
CONFIG_PATH = Path(__file__).parent.parent.parent.parent.parent / "config.yaml"

try:
    with open(CONFIG_PATH, "r") as f:
        config: Dict[str, Any] = yaml.safe_load(f)
except FileNotFoundError:
    # Si no existe config.yaml, usar valores por defecto y variables de entorno
    config = {
        "twilio": {
            "account_sid": os.getenv("TWILIO_ACCOUNT_SID"),
            "auth_token": os.getenv("TWILIO_AUTH_TOKEN"),
            "whatsapp_number": os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
        },
        "gcp": {
            "project_id": os.getenv("GOOGLE_CLOUD_PROJECT"),
            "region": os.getenv("REGION", "us-central1"),
            "firestore": {
                "collections": {
                    "knowledge_base": os.getenv("FIRESTORE_COLLECTION_KNOWLEDGE", "knowledge_base"),
                    "products": os.getenv("FIRESTORE_COLLECTION_PRODUCTS", "products"),
                    "faq": os.getenv("FIRESTORE_COLLECTION_FAQ", "faq"),
                    "chat_sessions": os.getenv("FIRESTORE_COLLECTION_SESSIONS", "chat_sessions")
                }
            }
        },
        "llm": {
            "model": os.getenv("LLM_MODEL", "mistral-tiny"),
            "api_keys": {
                "mistral": os.getenv("MISTRAL_API_KEY"),
                "openrouter": os.getenv("OPENROUTER_API_KEY"),
                "gemini": os.getenv("GEMINI_API_KEY")
            },
            "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7")),
            "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "200"))
        },
        "logging": {
            "level": os.getenv("LOG_LEVEL", "INFO")
        }
    }

# --- Extraer configuraciones específicas ---

# Twilio
twilio_config = config.get("twilio", {})
TWILIO_ACCOUNT_SID = twilio_config.get("account_sid")
TWILIO_AUTH_TOKEN = twilio_config.get("auth_token")
TWILIO_WHATSAPP_NUMBER = twilio_config.get("whatsapp_number", "whatsapp:+14155238886")

# GCP
gcp_config = config.get("gcp", {})
GOOGLE_CLOUD_PROJECT = gcp_config.get("project_id")
REGION = gcp_config.get("region", "us-central1")

# Firestore
firestore_config = gcp_config.get("firestore", {})
FIRESTORE_COLLECTION_KNOWLEDGE = firestore_config.get("collections", {}).get("knowledge_base", "knowledge_base")
FIRESTORE_COLLECTION_PRODUCTS = firestore_config.get("collections", {}).get("products", "products")
FIRESTORE_COLLECTION_FAQ = firestore_config.get("collections", {}).get("faq", "faq")
FIRESTORE_COLLECTION_SESSIONS = firestore_config.get("collections", {}).get("chat_sessions", "chat_sessions")
FIRESTORE_COLLECTION_RESPONSE_CACHE = firestore_config.get("collections", {}).get("response_cache", "response_cache")
FIRESTORE_COLLECTION_TOKEN_USAGE = firestore_config.get("collections", {}).get("token_usage", "token_usage")
FIRESTORE_COLLECTION_COMPLAINTS = firestore_config.get("collections", {}).get("complaints", "complaints")

# LLM
llm_config = config.get("llm", {})
LLM_MODEL = llm_config.get("model", "mistral-tiny")
MISTRAL_API_KEY = llm_config.get("api_keys", {}).get("mistral")
OPENROUTER_API_KEY = llm_config.get("api_keys", {}).get("openrouter")
GEMINI_API_KEY = llm_config.get("api_keys", {}).get("gemini")
LLM_TEMPERATURE = llm_config.get("temperature", 0.7)
LLM_MAX_TOKENS = llm_config.get("max_tokens", 200)
LLM_CACHING = llm_config.get("caching", True)
LLM_CACHE_EXPIRY_HOURS = llm_config.get("cache_expiry_hours", 1)

# Logging
logging_config = config.get("logging", {})
LOG_LEVEL = logging_config.get("level", "INFO")

# Monitoreo
monitoring_config = config.get("monitoring", {})
MAX_COST_PER_MONTH = monitoring_config.get("max_cost_per_month", 50)
ALERT_THRESHOLD = monitoring_config.get("alert_threshold", 40)

# Escalamiento
escalation_config = config.get("escalation", {})
NOTIFY_VIA_EMAIL = escalation_config.get("notify_via", {}).get("email", False)
NOTIFY_VIA_SLACK = escalation_config.get("notify_via", {}).get("slack", False)

# Email (si está configurado)
email_config = escalation_config.get("email", {})
SMTP_SERVER = email_config.get("smtp_server", "smtp.gmail.com")
SMTP_PORT = email_config.get("smtp_port", 587)
SMTP_USER = email_config.get("smtp_user")
SMTP_PASSWORD = email_config.get("smtp_password")
SUPPORT_EMAIL = email_config.get("support_email")

# Slack (si está configurado)
slack_config = escalation_config.get("slack", {})
SLACK_WEBHOOK_URL = slack_config.get("webhook_url")

# Testing
testing_config = config.get("testing", {})
USE_NGROK = testing_config.get("use_ngrok", True)
NGROK_PORT = testing_config.get("ngrok_port", 8000)

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
            f"Faltan variables de configuración obligatorias: {', '.join(missing_vars)}. "
            "Configúralas en el archivo config.yaml o en las variables de entorno."
        )
    
    # Validar que al menos una API key de LLM esté configurada
    llm_keys = [MISTRAL_API_KEY, OPENROUTER_API_KEY, GEMINI_API_KEY]
    if not any(llm_keys):
        raise ValueError(
            "No se encontró ninguna API key de LLM. "
            "Configura al menos una de: MISTRAL_API_KEY, OPENROUTER_API_KEY, GEMINI_API_KEY en config.yaml."
        )


# Validar configuración al importar el módulo
try:
    validate_config()
except ValueError as e:
    print(f"⚠️  Advertencia: {e}")
