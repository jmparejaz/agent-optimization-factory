# 📡 Flujo del Webhook de WhatsApp

## 🎯 **Objetivo**
Este documento describe el **flujo completo del webhook de WhatsApp**, desde que un cliente envía un mensaje hasta que recibe una respuesta generada por el agente. Incluye:
1. **Configuración del webhook en Twilio**.
2. **Estructura del backend en Cloud Run**.
3. **Procesamiento de mensajes**.
4. **Generación de respuestas con LLM**.
5. **Manejo de errores y edge cases**.

---

## 📌 **1. Configuración del Webhook en Twilio**

### **1.1. Requisitos Previos**
- Cuenta en [Twilio](https://www.twilio.com/) con **WhatsApp Sandbox** habilitado.
- Número de Twilio con WhatsApp activado (ej: `whatsapp:+14155238886`).
- **URL del backend** desplegado en Cloud Run (ej: `https://whatsapp-agent-backend.a.run.app/webhook`).

### **1.2. Pasos para Configurar el Webhook**
1. **Habilitar WhatsApp Sandbox**:
   - Ve a [Twilio Console > WhatsApp Sandbox](https://console.twilio.com/us1/develop/sms/sandbox).
   - Sigue las instrucciones para **unirte al sandbox** (enviar un mensaje al número de Twilio con el código de verificación).

2. **Configurar el Webhook**:
   - Ve a [Twilio Console > Phone Numbers > Manage > Active Numbers](https://console.twilio.com/us1/develop/phone-numbers/manage).
   - Selecciona tu número de WhatsApp.
   - En **"A MESSAGE COMES IN"**, configura:
     - **Webhook URL**: `https://<TU_DOMAIN>.a.run.app/webhook` (reemplaza `<TU_DOMAIN>`).
     - **HTTP Method**: `POST`.
     - **Webhook URL for Delivery Status**: (Opcional, dejar vacío).
   - Guarda los cambios.

3. **Probar el Webhook**:
   - Envía un mensaje de WhatsApp al número de Twilio.
   - Verifica que el backend reciba el mensaje (revisar logs en Cloud Run).

### **1.3. Ejemplo de Payload de Twilio**
Cuando un cliente envía un mensaje, Twilio envía un **POST** al webhook con el siguiente payload:
```json
{
  "To": "whatsapp:+14155238886",
  "From": "whatsapp:+521234567890",
  "Body": "Hola, ¿qué productos tienen?",
  "NumMedia": "0",
  "MessageSid": "SM1234567890abcdef",
  "SmsSid": "SM1234567890abcdef",
  "SmsStatus": "received",
  "ApiVersion": "2010-04-01"
}
```

**Campos importantes**:
- `From`: Número del cliente (incluye prefijo `whatsapp:`).
- `Body`: Contenido del mensaje.
- `MessageSid`: ID único del mensaje (útil para debugging).

---

## 📌 **2. Backend en Cloud Run (FastAPI)**

### **2.1. Estructura del Proyecto**
```bash
src/
├── main.py               # Backend principal (FastAPI)
├── models/
│   ├── twilio.py         # Modelo para mensajes de Twilio
│   └── response.py       # Modelo para respuestas
├── services/
│   ├── whatsapp.py       # Lógica de WhatsApp (Twilio)
│   ├── llm.py            # Integración con Mistral/OpenRouter
│   ├── knowledge_base.py # Acceso a Firestore (base de conocimiento)
│   └── session.py         # Manejo de sesiones de chat
├── utils/
│   ├── logging.py        # Configuración de logs
│   └── config.py         # Configuración de variables de entorno
└── requirements.txt       # Dependencias
```

### **2.2. Código Base del Backend (`main.py`)**
```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse
from services.whatsapp import process_message
from utils.logging import logger

app = FastAPI()

@app.post("/webhook", response_class=PlainTextResponse)
async def webhook(request: Request):
    try:
        # Parsear datos de Twilio
        form_data = await request.form()
        message_body = form_data.get("Body", "").strip()
        sender = form_data.get("From", "")
        message_sid = form_data.get("MessageSid", "")
        
        logger.info(f"Mensaje recibido de {sender}: {message_body}")
        
        # Procesar mensaje y generar respuesta
        response_text = await process_message(sender, message_body)
        
        # Crear respuesta para Twilio
        twiml = MessagingResponse()
        twiml.message(response_text)
        
        logger.info(f"Respuesta enviada a {sender}: {response_text}")
        return str(twiml)
        
    except Exception as e:
        logger.error(f"Error en webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### **2.3. Dependencias (`requirements.txt`)**
```text
fastapi==0.109.0
uvicorn==0.27.0
python-multipart==0.0.6
twilio==9.0.0
google-cloud-firestore==2.11.1
requests==2.31.0
python-dotenv==1.0.0
pydantic==2.5.3
```

---

## 📌 **3. Procesamiento de Mensajes**

### **3.1. Flujo de Procesamiento (`services/whatsapp.py`)**
```python
from services.llm import generate_response
from services.knowledge_base import get_knowledge_context
from services.session import save_message, get_session_context
from utils.logging import logger

async def process_message(sender: str, message: str) -> str:
    """
    Procesa un mensaje de WhatsApp y genera una respuesta.
    
    Args:
        sender: Número del cliente (ej: "whatsapp:+521234567890").
        message: Contenido del mensaje.
    
    Returns:
        str: Respuesta generada para el cliente.
    """
    try:
        # 1. Obtener contexto de la sesión (mensajes anteriores)
        session_context = await get_session_context(sender)
        
        # 2. Obtener contexto de la base de conocimiento
        knowledge_context = await get_knowledge_context()
        
        # 3. Generar respuesta con LLM
        response = await generate_response(
            message=message,
            session_context=session_context,
            knowledge_context=knowledge_context
        )
        
        # 4. Guardar mensaje y respuesta en la sesión
        await save_message(sender, "user", message)
        await save_message(sender, "assistant", response)
        
        return response
        
    except Exception as e:
        logger.error(f"Error procesando mensaje de {sender}: {e}", exc_info=True)
        return "Lo siento, hubo un error. Por favor, inténtalo de nuevo más tarde."
```

### **3.2. Manejo de Sesiones (`services/session.py`)**
```python
from google.cloud import firestore
from datetime import datetime, timedelta
from utils.config import FIRESTORE_COLLECTION_SESSIONS

# Inicializar cliente de Firestore
firestore_client = firestore.Client()

async def get_session_context(sender: str) -> list:
    """
    Recupera el historial de mensajes de una sesión.
    
    Args:
        sender: Número del cliente.
    
    Returns:
        list: Lista de mensajes anteriores (últimos 10 para contexto).
    """
    session_ref = firestore_client.collection(FIRESTORE_COLLECTION_SESSIONS).document(sender)
    session_doc = session_ref.get()
    
    if not session_doc.exists:
        return []
    
    messages = session_doc.to_dict().get("messages", [])
    # Retornar últimos 10 mensajes para contexto
    return messages[-10:] if len(messages) > 10 else messages

async def save_message(sender: str, role: str, content: str) -> None:
    """
    Guarda un mensaje en la sesión del cliente.
    
    Args:
        sender: Número del cliente.
        role: "user" o "assistant".
        content: Contenido del mensaje.
    """
    session_ref = firestore_client.collection(FIRESTORE_COLLECTION_SESSIONS).document(sender)
    
    # Crear o actualizar sesión
    session_ref.set({
        "last_updated": datetime.utcnow().isoformat(),
        "messages": firestore.ArrayUnion([{
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }])
    }, merge=True)
    
    # Eliminar sesiones inactivas (más de 1 hora)
    await cleanup_old_sessions()

async def cleanup_old_sessions() -> None:
    """Elimina sesiones inactivas (más de 1 hora)."""
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    sessions_ref = firestore_client.collection(FIRESTORE_COLLECTION_SESSIONS)
    
    # Filtrar sesiones no actualizadas en la última hora
    old_sessions = sessions_ref.where("last_updated", "<", one_hour_ago.isoformat())
    for doc in old_sessions.stream():
        doc.reference.delete()
```

---

## 📌 **4. Integración con LLM (Mistral/OpenRouter)**

### **4.1. Cliente de LLM (`services/llm.py`)**
```python
import requests
from utils.config import MISTRAL_API_KEY, OPENROUTER_API_KEY, LLM_MODEL
from utils.logging import logger

async def generate_response(message: str, session_context: list, knowledge_context: dict) -> str:
    """
    Genera una respuesta usando el LLM (Mistral/OpenRouter).
    
    Args:
        message: Mensaje del usuario.
        session_context: Historial de mensajes anteriores.
        knowledge_context: Contexto de la base de conocimiento.
    
    Returns:
        str: Respuesta generada por el LLM.
    """
    try:
        # Construir prompt con contexto
        prompt = build_prompt(message, session_context, knowledge_context)
        
        # Llamar al LLM (Mistral u OpenRouter)
        if LLM_MODEL.startswith("mistral"):
            response = await call_mistral_api(prompt)
        elif LLM_MODEL.startswith("openrouter"):
            response = await call_openrouter_api(prompt)
        else:
            response = "Lo siento, modelo de LLM no configurado."
        
        return response
        
    except Exception as e:
        logger.error(f"Error generando respuesta con LLM: {e}", exc_info=True)
        return "Lo siento, no pude generar una respuesta. Por favor, inténtalo de nuevo."

def build_prompt(message: str, session_context: list, knowledge_context: dict) -> str:
    """Construye el prompt para el LLM con contexto."""
    # Formatear historial de la sesión
    history = "\n".join([
        f"{msg['role']}: {msg['content']}" 
        for msg in session_context
    ])
    
    # Formatear base de conocimiento
    company_info = knowledge_context.get("company", {})
    products = knowledge_context.get("products", [])
    faq = knowledge_context.get("faq", [])
    
    knowledge_str = f"""
    --- Contexto de la Empresa ---
    Nombre: {company_info.get('name', 'N/A')}
    Descripción: {company_info.get('description', 'N/A')}
    
    --- Productos ---
    {chr(10).join([f"- {p['name']}: {p['description']} (Precio: ${p['price']})" for p in products])}
    
    --- Preguntas Frecuentes ---
    {chr(10).join([f"Q: {q['question']} A: {q['answer']}" for q in faq])}
    """
    
    # Prompt final
    return f"""
    Eres un asistente de ventas y servicio al cliente de {company_info.get('name', 'la empresa')}. 
    Tu objetivo es responder preguntas de los clientes de manera clara y útil, 
    basándote en el contexto proporcionado.
    
    --- Contexto de la Conversación ---
    {history}
    
    --- Contexto de la Empresa ---
    {knowledge_str}
    
    --- Pregunta del Cliente ---
    {message}
    
    --- Instrucciones ---
    1. Responde en español.
    2. Sé claro y conciso (máximo 200 palabras).
    3. Si no sabes la respuesta, di: "No tengo esa información, pero puedo derivarte a un agente humano."
    4. No inventes información.
    
    Respuesta:
    """

async def call_mistral_api(prompt: str) -> str:
    """Llama a la API de Mistral."""
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 200
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    response.raise_for_status()
    
    return response.json()["choices"][0]["message"]["content"]

async def call_openrouter_api(prompt: str) -> str:
    """Llama a la API de OpenRouter."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 200
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    response.raise_for_status()
    
    return response.json()["choices"][0]["message"]["content"]
```

### **4.2. Configuración del LLM (`utils/config.py`)**
```python
import os
from dotenv import load_dotenv

load_dotenv()

# --- Configuración de Twilio ---
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# --- Configuración de Firestore ---
FIRESTORE_COLLECTION_KNOWLEDGE = "knowledge_base"
FIRESTORE_COLLECTION_SESSIONS = "chat_sessions"
FIRESTORE_COLLECTION_PRODUCTS = "products"
FIRESTORE_COLLECTION_FAQ = "faq"

# --- Configuración del LLM ---
# Opciones: "mistral-tiny", "mistral-small", "openrouter:mistralai/mistral-tiny"
LLM_MODEL = os.getenv("LLM_MODEL", "mistral-tiny")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# --- Configuración de Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
```

---

## 📌 **5. Base de Conocimiento (`services/knowledge_base.py`)**

### **5.1. Acceso a Firestore**
```python
from google.cloud import firestore
from utils.config import (
    FIRESTORE_COLLECTION_KNOWLEDGE,
    FIRESTORE_COLLECTION_PRODUCTS,
    FIRESTORE_COLLECTION_FAQ
)

firestore_client = firestore.Client()

async def get_knowledge_context() -> dict:
    """
    Recupera toda la base de conocimiento (empresa, productos, FAQ).
    
    Returns:
        dict: Contexto completo para el LLM.
    """
    # Obtener información de la empresa
    company_ref = firestore_client.collection(FIRESTORE_COLLECTION_KNOWLEDGE).document("company")
    company_doc = company_ref.get()
    company_info = company_doc.to_dict() if company_doc.exists else {}
    
    # Obtener productos
    products_ref = firestore_client.collection(FIRESTORE_COLLECTION_PRODUCTS)
    products = [doc.to_dict() for doc in products_ref.stream()]
    
    # Obtener FAQ
    faq_ref = firestore_client.collection(FIRESTORE_COLLECTION_FAQ)
    faq = [doc.to_dict() for doc in faq_ref.stream()]
    
    return {
        "company": company_info,
        "products": products,
        "faq": faq
    }
```

### **5.2. Ejemplo de Datos en Firestore**

**Colección `knowledge_base` (documento `company`)**:
```json
{
  "name": "Mi Empresa",
  "description": "Somos una empresa dedicada a la venta de productos innovadores para el hogar.",
  "mission": "Ofrecer soluciones prácticas y de alta calidad.",
  "vision": "Ser líderes en el mercado con productos sostenibles."
}
```

**Colección `products`**:
```json
[
  {
    "name": "Producto 1",
    "description": "Un producto revolucionario para el hogar.",
    "price": 100,
    "features": ["Duradero", "Fácil de usar", "Ecológico"]
  },
  {
    "name": "Producto 2",
    "description": "La solución definitiva para tus necesidades.",
    "price": 150,
    "features": ["Rápido", "Eficiente", "Garantía de 1 año"]
  }
]
```

**Colección `faq`**:
```json
[
  {
    "question": "¿Cuál es el precio del Producto 1?",
    "answer": "El precio del Producto 1 es $100."
  },
  {
    "question": "¿Ofrecen garantía?",
    "answer": "Sí, todos nuestros productos tienen garantía de 1 año."
  }
]
```

---

## 📌 **6. Manejo de Errores y Edge Cases**

### **6.1. Errores Comunes y Soluciones**
| **Error**                          | **Causa**                                  | **Solución**                                                                 |
|-----------------------------------|-------------------------------------------|------------------------------------------------------------------------------|
| **Twilio no envía mensajes**      | Webhook mal configurado.                  | Verificar URL del webhook en Twilio Console.                                |
| **Cloud Run no recibe mensajes**  | Permisos o firewall.                       | Asegurar que Cloud Run esté accesible públicamente.                        |
| **LLM no responde**               | API key inválida o cuota agotada.          | Verificar API key y saldo en Mistral/OpenRouter.                           |
| **Firestore no guarda datos**     | Permisos de IAM.                          | Asegurar que el servicio de Cloud Run tenga permisos de Firestore.         |
| **Respuestas genéricas**          | Prompt mal diseñado.                      | Mejorar el prompt con más contexto.                                         |

### **6.2. Código para Manejo de Errores**
```python
from fastapi import HTTPException
from utils.logging import logger

async def safe_process_message(sender: str, message: str) -> str:
    """Procesa un mensaje con manejo de errores."""
    try:
        return await process_message(sender, message)
    except Exception as e:
        logger.error(f"Error crítico en process_message: {e}", exc_info=True)
        return "Lo siento, hubo un error. Por favor, contacta a soporte técnico."

# Ejemplo de uso en el webhook:
@app.post("/webhook")
async def webhook(request: Request):
    try:
        form_data = await request.form()
        message = form_data.get("Body", "")
        sender = form_data.get("From", "")
        
        if not message or not sender:
            raise HTTPException(status_code=400, detail="Mensaje o remitente vacío")
        
        response = await safe_process_message(sender, message)
        twiml = MessagingResponse()
        twiml.message(response)
        return str(twiml)
        
    except HTTPException as e:
        logger.error(f"HTTP Error: {e.detail}")
        twiml = MessagingResponse()
        twiml.message("Error: " + e.detail)
        return str(twiml)
    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        twiml = MessagingResponse()
        twiml.message("Error interno. Por favor, inténtalo más tarde.")
        return str(twiml)
```

---

## 📌 **7. Pruebas del Webhook**

### **7.1. Pruebas Locales con ngrok**
1. **Instalar ngrok**:
   ```bash
   # Linux/Mac
   curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
   echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
   sudo apt update && sudo apt install ngrok
   
   # Windows (Chocolatey)
   choco install ngrok
   ```

2. **Iniciar ngrok**:
   ```bash
   ngrok http 8000
   ```
   - Esto generará una URL pública como `https://abc123.ngrok.io`.

3. **Configurar Twilio**:
   - En Twilio Console, configura el webhook con la URL de ngrok: `https://abc123.ngrok.io/webhook`.

4. **Iniciar el backend localmente**:
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```

5. **Probar el webhook**:
   - Envía un mensaje de WhatsApp al número de Twilio.
   - Verifica que el backend reciba el mensaje y responda.

### **7.2. Pruebas con cURL**
Puedes simular un mensaje de Twilio con cURL:
```bash
curl -X POST http://localhost:8000/webhook \
  -d "Body=Hola%2C+%C2%BFqu%C3%A9+productos+tienen%3F" \
  -d "From=whatsapp%3A%2B521234567890" \
  -d "To=whatsapp%3A%2B14155238886" \
  -d "MessageSid=SM1234567890abcdef"
```

**Respuesta esperada**:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Respuesta generada por el LLM...</Message>
</Response>
```

---

## 📌 **8. Despliegue en Cloud Run**

### **8.1. Construir y Desplegar el Contenedor**
1. **Crear `Dockerfile`**:
   ```dockerfile
   FROM python:3.10-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
   ```

2. **Construir la imagen**:
   ```bash
   gcloud builds submit --tag gcr.io/[PROJECT_ID]/whatsapp-agent-backend
   ```

3. **Desplegar en Cloud Run**:
   ```bash
   gcloud run deploy whatsapp-agent-backend \
     --image gcr.io/[PROJECT_ID]/whatsapp-agent-backend \
     --platform managed \
     --region us-central1 \
     --memory 2Gi \
     --cpu 1 \
     --max-instances 1 \
     --allow-unauthenticated \
     --set-env-vars "TWILIO_ACCOUNT_SID=tu_sid,TWILIO_AUTH_TOKEN=tu_token,MISTRAL_API_KEY=tu_api_key"
   ```

4. **Configurar el webhook en Twilio**:
   - Actualiza la URL del webhook en Twilio Console con la URL de Cloud Run (ej: `https://whatsapp-agent-backend.a.run.app/webhook`).

---

## 📌 **9. Monitoreo y Logging**

### **9.1. Configuración de Logging (`utils/logging.py`)**
```python
import logging
from pythonjsonlogger import jsonlogger
from utils.config import LOG_LEVEL

# Configurar logger en formato JSON para Cloud Logging
logger = logging.getLogger(__name__)

def setup_logging():
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s %(funcName)s %(lineno)d"
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.setLevel(LOG_LEVEL)
    return logger

# Inicializar logger
logger = setup_logging()
```

### **9.2. Consultar Logs en Cloud Logging**
1. Ve a [Cloud Logging](https://console.cloud.google.com/logs) en GCP Console.
2. Filtra por el **nombre del servicio de Cloud Run** (`whatsapp-agent-backend`).
3. Busca logs con:
   - `level=ERROR` (para errores).
   - `message="Mensaje recibido"` (para mensajes entrantes).

### **9.3. Métricas Clave a Monitorear**
| **Métrica**               | **Herramienta**          | **Objetivo**               |
|---------------------------|--------------------------|----------------------------|
| Tiempo de respuesta       | Cloud Monitoring         | < 5 segundos               |
| Número de mensajes        | Cloud Logging            | ~100 usuarios/día          |
| Errores del backend       | Cloud Logging            | 0 errores críticos         |
| Uso de tokens (LLM)       | Logs personalizados      | ≤ 10K tokens/día           |
| Costo mensual             | GCP Billing Dashboard     | ≤ $50                      |

---

## 📌 **10. Optimizaciones Recomendadas**

### **10.1. Caching de Respuestas Frecuentes**
- **Problema**: El LLM se llamará repetidamente para las mismas preguntas (ej: "¿Cuál es el precio del Producto 1?").
- **Solución**: Guardar respuestas frecuentes en Firestore o Redis.
  ```python
  # Ejemplo de caching en Firestore
  async def get_cached_response(prompt: str) -> str | None:
      cache_ref = firestore_client.collection("response_cache").document(prompt)
      cache_doc = cache_ref.get()
      if cache_doc.exists:
          return cache_doc.to_dict()["response"]
      return None
  
  async def cache_response(prompt: str, response: str) -> None:
      cache_ref = firestore_client.collection("response_cache").document(prompt)
      cache_ref.set({"response": response, "timestamp": datetime.utcnow().isoformat()})
  ```

### **10.2. Limitar Longitud de Respuestas**
- **Problema**: Respuestas largas aumentan el costo de tokens.
- **Solución**: Limitar a **200 tokens** por respuesta.
  ```python
  # En la llamada al LLM:
  payload = {
      "model": LLM_MODEL,
      "messages": [{"role": "user", "content": prompt}],
      "max_tokens": 200  # Límites a 200 tokens
  }
  ```

### **10.3. Usar Modelos Más Económicos**
- **Mistral Tiny**: ~$0.00000025/token (input) + $0.0000005/token (output).
- **Mistral Small**: ~$0.0000008/token (input) + $0.0000024/token (output).
- **Recomendación**: Usar **Mistral Tiny** para mantener costos bajos.

---

## 📌 **Resumen de Archivos Clave**
| **Archivo**                     | **Descripción**                                                                 |
|--------------------------------|---------------------------------------------------------------------------------|
| `src/main.py`                  | Backend principal (FastAPI).                                                   |
| `src/services/whatsapp.py`     | Lógica de procesamiento de mensajes.                                           |
| `src/services/llm.py`          | Integración con Mistral/OpenRouter.                                            |
| `src/services/session.py`      | Manejo de sesiones de chat.                                                     |
| `src/services/knowledge_base.py` | Acceso a la base de conocimiento en Firestore.                                |
| `src/utils/config.py`          | Configuración de variables de entorno.                                          |
| `src/utils/logging.py`         | Configuración de logging.                                                      |
| `requirements.txt`             | Dependencias del proyecto.                                                     |
| `Dockerfile`                   | Configuración para construir el contenedor.                                    |

---

## 📅 **Historial de Cambios**
| **Versión** | **Fecha**       | **Autor**               | **Cambios**                                  |
|-------------|-----------------|-------------------------|---------------------------------------------|
| 1.0         | 2024-10-01      | Equipo de Desarrollo    | Versión inicial con flujo completo.        |

---

## 🚀 **Próximos Pasos**
1. **Configurar Twilio y GCP** (Fase 1).
2. **Desarrollar el backend** con los archivos descritos.
3. **Probar localmente** con ngrok.
4. **Desplegar en Cloud Run** y validar con mensajes reales.

**¿Listo para implementar este flujo?** ✅
