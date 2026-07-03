# 🚀 Backend Principal del Agente de WhatsApp
# Este archivo es el punto de entrada del backend, implementado con FastAPI.

import os
import yaml
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional, Dict, Any
from pathlib import Path

# Cargar configuración desde config.yaml
CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

try:
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    raise RuntimeError(
        f"No se encontró el archivo de configuración en {CONFIG_PATH}. "
        "Asegúrate de que config.yaml existe y está en el directorio raíz del proyecto."
    )
except yaml.YAMLError as e:
    raise RuntimeError(f"Error al cargar config.yaml: {e}")

# Inicializar FastAPI
app = FastAPI(
    title="Agente de WhatsApp para Servicio al Cliente y Ventas",
    description="Backend para un agente de WhatsApp que automatiza servicio al cliente y ventas.",
    version="1.0.0"
)

# Montar directorio estático (opcional, para documentación)
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- Importar módulos de skills ---
from agents.skills.whatsapp_handler import WhatsAppHandler
from agents.skills.response_generator import ResponseGenerator
from agents.skills.session_manager import SessionManager
from agents.skills.knowledge_base import KnowledgeBase
from agents.skills.llm_client import LLMClient
from agents.skills.utils.logging import logger
from agents.skills.utils.config import validate_config

# Validar configuración al iniciar
try:
    validate_config()
except ValueError as e:
    logger.error(f"Error de configuración: {e}")
    raise

# Inicializar componentes
whatsapp_handler = WhatsAppHandler()
response_generator = ResponseGenerator()
session_manager = SessionManager()
knowledge_base = KnowledgeBase()
llm_client = LLMClient(model=config["llm"]["model"])


# --- Endpoints ---

@app.post("/webhook", response_class=PlainTextResponse)
async def webhook(request: Request):
    """
    Endpoint principal para recibir mensajes de WhatsApp vía Twilio.
    
    Este endpoint:
    1. Recibe mensajes de Twilio.
    2. Procesa el mensaje con el agente.
    3. Genera una respuesta usando el LLM y la base de conocimiento.
    4. Envía la respuesta de vuelta al cliente.
    """
    try:
        # Validar webhook (opcional: implementar validación de firma de Twilio)
        if not whatsapp_handler.validate_webhook(request):
            logger.warning("Solicitud de webhook no válida.")
            return whatsapp_handler.generate_twiml_response("Error: Solicitud no válida.")
        
        # Recibir mensaje de Twilio
        message_data = await whatsapp_handler.receive_message(request)
        if not message_data:
            return whatsapp_handler.generate_twiml_response("Error: No se pudo procesar el mensaje.")
        
        # Extraer datos del mensaje
        message_body = message_data.get("Body", "")
        sender = message_data.get("From", "")
        message_sid = message_data.get("MessageSid", "")
        
        if not message_body or not sender:
            logger.error(f"Mensaje vacío o remitente vacío. MessageSid: {message_sid}")
            return whatsapp_handler.generate_twiml_response("Error: Mensaje vacío.")
        
        logger.info(f"Mensaje recibido de {sender}: {message_body}")
        
        # Generar respuesta usando el generador de respuestas
        response_text = await response_generator.generate_response(sender, message_body)
        
        # Guardar mensaje y respuesta en la sesión
        await session_manager.save_message(sender, "user", message_body)
        await session_manager.save_message(sender, "assistant", response_text)
        
        logger.info(f"Respuesta generada para {sender}: {response_text[:100]}...")
        
        # Generar respuesta en formato TwiML para Twilio
        return whatsapp_handler.generate_twiml_response(response_text)
        
    except HTTPException as e:
        logger.error(f"HTTP Error: {e.detail}")
        return whatsapp_handler.generate_twiml_response(f"Error: {e.detail}")
    except Exception as e:
        logger.error(f"Error inesperado en webhook: {e}", exc_info=True)
        return whatsapp_handler.generate_twiml_response(
            "Lo siento, hubo un error interno. Por favor, inténtalo más tarde."
        )


@app.get("/health", response_class=JSONResponse)
async def health_check():
    """
    Endpoint para verificar el estado del servicio.
    """
    return {
        "status": "healthy",
        "service": config["gcp"]["cloud_run"]["service_name"],
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/config", response_class=JSONResponse)
async def get_config():
    """
    Endpoint para obtener la configuración actual (solo para desarrollo).
    """
    # Filtrar datos sensibles (API keys, tokens)
    safe_config = config.copy()
    
    # Eliminar API keys
    if "llm" in safe_config and "api_keys" in safe_config["llm"]:
        safe_config["llm"]["api_keys"] = {
            "mistral": "***" if safe_config["llm"]["api_keys"].get("mistral") else None,
            "openrouter": "***" if safe_config["llm"]["api_keys"].get("openrouter") else None,
            "gemini": "***" if safe_config["llm"]["api_keys"].get("gemini") else None
        }
    
    # Eliminar tokens de Twilio
    if "twilio" in safe_config:
        safe_config["twilio"]["account_sid"] = "***" if safe_config["twilio"].get("account_sid") else None
        safe_config["twilio"]["auth_token"] = "***" if safe_config["twilio"].get("auth_token") else None
    
    return {"config": safe_config}


@app.post("/test/llm", response_class=JSONResponse)
async def test_llm(request: Request):
    """
    Endpoint para probar la integración con el LLM (solo para desarrollo).
    """
    try:
        data = await request.json()
        prompt = data.get("prompt", "")
        
        if not prompt:
            return {"error": "El campo 'prompt' es obligatorio."}
        
        # Obtener contexto de la base de conocimiento
        knowledge_context = await knowledge_base.get_knowledge_context()
        
        # Generar respuesta con el LLM
        response = await llm_client.generate_response(
            message=prompt,
            session_context=[],  # Sin contexto para prueba
            knowledge_context=knowledge_context
        )
        
        return {
            "prompt": prompt,
            "response": response,
            "model": config["llm"]["model"]
        }
        
    except Exception as e:
        logger.error(f"Error en test_llm: {e}", exc_info=True)
        return {"error": str(e)}


@app.post("/test/knowledge-base", response_class=JSONResponse)
async def test_knowledge_base():
    """
    Endpoint para probar el acceso a la base de conocimiento (solo para desarrollo).
    """
    try:
        knowledge_context = await knowledge_base.get_knowledge_context()
        return {
            "knowledge_base": knowledge_context
        }
    except Exception as e:
        logger.error(f"Error en test_knowledge_base: {e}", exc_info=True)
        return {"error": str(e)}


# --- Inicialización ---
from datetime import datetime

@app.on_event("startup")
async def startup_event():
    """
    Acciones a realizar al iniciar el servicio.
    """
    logger.info("🚀 Iniciando servicio de Agente de WhatsApp...")
    logger.info(f"Modelo de LLM: {config['llm']['model']}")
    logger.info(f"Proyecto GCP: {config['gcp']['project_id']}")
    logger.info(f"Servicio Cloud Run: {config['gcp']['cloud_run']['service_name']}")
    
    # Validar conexión a Firestore
    try:
        test_doc = firestore.Client().collection("test").document("test")
        test_doc.set({"timestamp": datetime.utcnow().isoformat()})
        test_doc.delete()
        logger.info("✅ Conexión a Firestore validada.")
    except Exception as e:
        logger.error(f"❌ Error al conectar a Firestore: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Acciones a realizar al detener el servicio.
    """
    logger.info("🛑 Deteniendo servicio de Agente de WhatsApp...")


# --- Ejecutar la aplicación ---
if __name__ == "__main__":
    import uvicorn
    
    # Configurar uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=config["logging"]["level"].lower()
    )
