# 🤖 Integración con LLM (Mistral/OpenRouter/Gemini)

## 🎯 **Objetivo**
Este documento detalla cómo integrar el **agente de WhatsApp** con **Mistral API**, **OpenRouter API** o **Gemini API** para generar respuestas dinámicas y contextualizadas. Incluye:
1. **Configuración de APIs** (claves, modelos, costos).
2. **Diseño de prompts** (cómo estructurar las solicitudes al LLM).
3. **Manejo de contexto** (sesiones de chat, base de conocimiento).
4. **Optimización de costos** (caching, límites de tokens).
5. **Ejemplos de código** para cada API.

---

## 📌 **1. Comparación de APIs de LLM**

| **API**          | **Modelos Disponibles**               | **Costo (Input)**       | **Costo (Output)**      | **Ventajas**                          | **Desventajas**                     |
|------------------|--------------------------------------|-------------------------|-------------------------|---------------------------------------|-------------------------------------|
| **Mistral API**  | `mistral-tiny`, `mistral-small`, `mistral-medium` | ~$0.00000025/token | ~$0.0000005/token | Más económico, buen rendimiento.      | Menos modelos que OpenRouter.        |
| **OpenRouter API** | `mistralai/mistral-tiny`, `google/gemini-pro`, `anthropic/claude-3-haiku` | Varía por modelo | Varía por modelo | Acceso a múltiples modelos.          | Requiere configuración adicional.   |
| **Gemini API**   | `gemini-1.0-pro`, `gemini-1.5-pro`    | ~$0.000005/token        | ~$0.000016/token        | Integración nativa con GCP.          | Más caro que Mistral.                |

**Recomendación**:
- **Priorizar Mistral API** (más económico y suficiente para el caso de uso).
- **Usar OpenRouter** si se quiere flexibilidad para cambiar de modelo luego.
- **Evitar Gemini** en esta fase (costo más alto).

---

## 📌 **2. Configuración de APIs**

### **2.1. Mistral API**

#### **Pasos para Obtener API Key**
1. Regístrate en [Mistral AI](https://mistral.ai/).
2. Ve a [Console > API Keys](https://console.mistral.ai/api-keys/).
3. Crea una nueva API key y guárdala en un lugar seguro.

#### **Modelos Disponibles**
| **Modelo**          | **Descripción**                          | **Costo (Input)** | **Costo (Output)** | **Contexto Máximo** |
|---------------------|------------------------------------------|-------------------|--------------------|--------------------|
| `mistral-tiny`      | Modelo pequeño y rápido.                | $0.00000025/token | $0.0000005/token   | 32K tokens          |
| `mistral-small`     | Modelo mediano.                         | $0.0000008/token  | $0.0000024/token   | 32K tokens          |
| `mistral-medium`    | Modelo grande (mejor precisión).         | $0.0000025/token  | $0.0000075/token   | 32K tokens          |

**Recomendación**: Usar `mistral-tiny` para mantener costos bajos.

#### **Ejemplo de Código (Mistral API)**
```python
import requests
from typing import Optional

MISTRAL_API_KEY = "tu_api_key_de_mistral"
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

async def call_mistral_api(
    prompt: str,
    model: str = "mistral-tiny",
    temperature: float = 0.7,
    max_tokens: int = 200
) -> Optional[str]:
    """
    Llama a la API de Mistral para generar una respuesta.
    
    Args:
        prompt: Mensaje del usuario + contexto.
        model: Modelo de Mistral a usar (ej: "mistral-tiny").
        temperature: Creatividad (0 = determinista, 1 = aleatorio).
        max_tokens: Máximo de tokens en la respuesta.
    
    Returns:
        str: Respuesta generada por el LLM, o None si hay error.
    """
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(MISTRAL_API_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"Error llamando a Mistral API: {e}")
        return None
```

---

### **2.2. OpenRouter API**

#### **Pasos para Obtener API Key**
1. Regístrate en [OpenRouter](https://openrouter.ai/).
2. Ve a [Account > API Keys](https://openrouter.ai/keys).
3. Crea una nueva API key.

#### **Modelos Disponibles**
Puedes usar cualquier modelo disponible en OpenRouter, incluyendo:
- `mistralai/mistral-tiny`
- `mistralai/mistral-small`
- `google/gemini-pro`
- `anthropic/claude-3-haiku`

**Recomendación**: Usar `mistralai/mistral-tiny` para mantener costos bajos.

#### **Ejemplo de Código (OpenRouter API)**
```python
import requests
from typing import Optional

OPENROUTER_API_KEY = "tu_api_key_de_openrouter"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

async def call_openrouter_api(
    prompt: str,
    model: str = "mistralai/mistral-tiny",
    temperature: float = 0.7,
    max_tokens: int = 200
) -> Optional[str]:
    """
    Llama a la API de OpenRouter para generar una respuesta.
    
    Args:
        prompt: Mensaje del usuario + contexto.
        model: Modelo a usar (ej: "mistralai/mistral-tiny").
        temperature: Creatividad (0 = determinista, 1 = aleatorio).
        max_tokens: Máximo de tokens en la respuesta.
    
    Returns:
        str: Respuesta generada por el LLM, o None si hay error.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(OPENROUTER_API_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        print(f"Error llamando a OpenRouter API: {e}")
        return None
```

---

### **2.3. Gemini API (Google)**

#### **Pasos para Obtener API Key**
1. Ve a [Google Cloud Console](https://console.cloud.google.com/).
2. Habilita la API de **Vertex AI** (si no está habilitada).
3. Ve a [Vertex AI > Credentials](https://console.cloud.google.com/apis/credentials) y crea una API key.

#### **Modelos Disponibles**
| **Modelo**          | **Descripción**                          | **Costo (Input)** | **Costo (Output)** | **Contexto Máximo** |
|---------------------|------------------------------------------|-------------------|--------------------|--------------------|
| `gemini-1.0-pro`    | Modelo principal de Gemini.             | $0.000005/token   | $0.000016/token    | 32K tokens          |
| `gemini-1.5-pro`    | Modelo mejorado (más preciso).          | $0.000007/token   | $0.000021/token    | 1M tokens           |

**Nota**: Gemini API es más caro que Mistral, pero tiene integración nativa con GCP.

#### **Ejemplo de Código (Gemini API)**
```python
import requests
from typing import Optional

GEMINI_API_KEY = "tu_api_key_de_gemini"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"

async def call_gemini_api(
    prompt: str,
    model: str = "gemini-1.0-pro",
    temperature: float = 0.7,
    max_tokens: int = 200
) -> Optional[str]:
    """
    Llama a la API de Gemini para generar una respuesta.
    
    Args:
        prompt: Mensaje del usuario + contexto.
        model: Modelo de Gemini a usar (ej: "gemini-1.0-pro").
        temperature: Creatividad (0 = determinista, 1 = aleatorio).
        max_tokens: Máximo de tokens en la respuesta.
    
    Returns:
        str: Respuesta generada por el LLM, o None si hay error.
    """
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens
        }
    }
    
    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}",
            json=payload,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except requests.exceptions.RequestException as e:
        print(f"Error llamando a Gemini API: {e}")
        return None
```

---

## 📌 **3. Diseño de Prompts**

### **3.1. Estructura del Prompt**
El prompt debe incluir:
1. **Rol del LLM**: Definir que es un asistente de ventas.
2. **Contexto de la empresa**: Descripción, productos, FAQ.
3. **Historial de la conversación**: Mensajes anteriores para mantener contexto.
4. **Pregunta del usuario**: El mensaje actual.
5. **Instrucciones**: Reglas para la respuesta (idioma, longitud, estilo).

### **3.2. Ejemplo de Prompt**
```python
def build_prompt(
    message: str,
    session_context: list[dict],
    knowledge_context: dict
) -> str:
    """
    Construye el prompt para el LLM con contexto.
    
    Args:
        message: Mensaje actual del usuario.
        session_context: Historial de mensajes anteriores (lista de dicts con "role" y "content").
        knowledge_context: Contexto de la base de conocimiento (empresa, productos, FAQ).
    
    Returns:
        str: Prompt completo para el LLM.
    """
    # Formatear historial de la sesión
    history = "\n".join([
        f"{msg['role']}: {msg['content']}" 
        for msg in session_context
    ])
    
    # Formatear base de conocimiento
    company_info = knowledge_context.get("company", {})
    products = knowledge_context.get("products", [])
    faq = knowledge_context.get("faq", [])
    
    products_str = "\n".join([
        f"- {p['name']}: {p['description']} (Precio: ${p['price']})"
        for p in products
    ])
    
    faq_str = "\n".join([
        f"Q: {q['question']}\nA: {q['answer']}"
        for q in faq
    ])
    
    knowledge_str = f"""
    --- Contexto de la Empresa ---
    Nombre: {company_info.get('name', 'N/A')}
    Descripción: {company_info.get('description', 'N/A')}
    Misión: {company_info.get('mission', 'N/A')}
    Visión: {company_info.get('vision', 'N/A')}
    
    --- Productos Disponibles ---
    {products_str if products else "No hay productos configurados."}
    
    --- Preguntas Frecuentes ---
    {faq_str if faq else "No hay preguntas frecuentes configuradas."}
    """
    
    # Prompt final
    return f"""
    Eres un **asistente de ventas y servicio al cliente** de **{company_info.get('name', 'la empresa')}**. 
    Tu objetivo es responder preguntas de los clientes de manera **clara, útil y profesional**, 
    basándote **exclusivamente** en el contexto proporcionado a continuación.
    
    --- Contexto de la Conversación ---
    {history if history else "(No hay historial previo)"}
    
    --- Contexto de la Empresa y Productos ---
    {knowledge_str}
    
    --- Pregunta del Cliente ---
    {message}
    
    --- Instrucciones ---
    1. **Idioma**: Responde **siempre en español** (a menos que el cliente pregunte en otro idioma).
    2. **Longitud**: Sé **conciso** (máximo 200 palabras).
    3. **Precisión**: Si no tienes la información en el contexto, responde: 
       "No tengo esa información, pero puedo derivarte a un agente humano."
    4. **Formato**: Usa **negritas** para nombres de productos o términos importantes.
    5. **Tono**: Sé **amigable pero profesional**.
    6. **Contexto**: Usa el **historial de la conversación** para mantener coherencia.
    
    --- Ejemplo de Respuesta ---
    Cliente: ¿Cuál es el precio del Producto 1?
    Asistente: El precio del **Producto 1** es **$100**. Incluye garantía de 1 año.
    
    --- Tu Respuesta ---
    """
```

### **3.3. Ejemplo de Prompt para Preguntas Frecuentes**
Si el usuario pregunta algo que está en el FAQ, el LLM debe **priorizar la respuesta del FAQ** (aunque también pueda responder con su conocimiento general).

**Ejemplo**:
```text
Cliente: ¿Ofrecen garantía en sus productos?

Contexto de FAQ:
Q: ¿Ofrecen garantía?
A: Sí, todos nuestros productos tienen garantía de 1 año.

Respuesta esperada:
Sí, todos nuestros productos tienen **garantía de 1 año**.
```

### **3.4. Ejemplo de Prompt para Productos**
```text
Cliente: ¿Qué productos tienen para el hogar?

Contexto de Productos:
- Producto 1: Un producto revolucionario para el hogar. (Precio: $100)
- Producto 2: La solución definitiva para tus necesidades. (Precio: $150)

Respuesta esperada:
Tenemos los siguientes productos para el hogar:
- **Producto 1**: Un producto revolucionario para el hogar. **Precio: $100**.
- **Producto 2**: La solución definitiva para tus necesidades. **Precio: $150**.
```

---

## 📌 **4. Manejo de Contexto**

### **4.1. Contexto de la Sesión**
El **historial de la conversación** se usa para que el LLM **mantenga coherencia** en las respuestas. Por ejemplo:

**Ejemplo sin contexto**:
```text
Cliente: ¿Cuánto cuesta?
Asistente: ¿El qué? No entiendo tu pregunta.
```

**Ejemplo con contexto**:
```text
Cliente: ¿Qué productos tienen para el hogar?
Asistente: Tenemos el **Producto 1** ($100) y el **Producto 2** ($150).
Cliente: ¿Cuánto cuesta?
Asistente: El **Producto 1** cuesta **$100** y el **Producto 2** cuesta **$150**.
```

### **4.2. Implementación del Contexto**
```python
from typing import List, Dict

def get_session_context(sender: str, max_messages: int = 10) -> List[Dict]:
    """
    Recupera los últimos `max_messages` mensajes de una sesión.
    
    Args:
        sender: Número del cliente (ej: "whatsapp:+521234567890").
        max_messages: Número máximo de mensajes a recuperar.
    
    Returns:
        List[Dict]: Lista de mensajes (cada mensaje es un dict con "role" y "content").
    """
    # Ejemplo: Recuperar de Firestore
    session_ref = firestore_client.collection("chat_sessions").document(sender)
    session_doc = session_ref.get()
    
    if not session_doc.exists:
        return []
    
    messages = session_doc.to_dict().get("messages", [])
    return messages[-max_messages:]  # Retornar últimos `max_messages` mensajes
```

### **4.3. Límites del Contexto**
- **Mistral/OpenRouter**: Soporte hasta **32K tokens** de contexto (suficiente para ~100 mensajes).
- **Gemini**: Soporte hasta **1M tokens** (para `gemini-1.5-pro`).
- **Recomendación**: Limitar a **10 mensajes anteriores** para mantener costos bajos.

---

## 📌 **5. Optimización de Costos**

### **5.1. Caching de Respuestas**
**Problema**: El LLM se llamará repetidamente para las mismas preguntas (ej: "¿Cuál es el precio del Producto 1?").

**Solución**: Guardar respuestas frecuentes en **Firestore** o **Redis**.

#### **Implementación con Firestore**
```python
from google.cloud import firestore
from datetime import datetime, timedelta

firestore_client = firestore.Client()

async def get_cached_response(prompt: str) -> Optional[str]:
    """
    Busca una respuesta en caché para el prompt dado.
    
    Args:
        prompt: Prompt completo (incluyendo contexto).
    
    Returns:
        str: Respuesta en caché, o None si no existe.
    """
    # Usar un hash del prompt para evitar problemas con caracteres especiales
    prompt_hash = hash(prompt)
    cache_ref = firestore_client.collection("response_cache").document(str(prompt_hash))
    cache_doc = cache_ref.get()
    
    if cache_doc.exists:
        # Verificar si la caché está vigente (ej: menos de 1 hora)
        timestamp = cache_doc.to_dict().get("timestamp")
        if timestamp and datetime.fromisoformat(timestamp) > datetime.utcnow() - timedelta(hours=1):
            return cache_doc.to_dict()["response"]
    
    return None

async def cache_response(prompt: str, response: str) -> None:
    """
    Guarda una respuesta en caché.
    
    Args:
        prompt: Prompt completo.
        response: Respuesta generada por el LLM.
    """
    prompt_hash = hash(prompt)
    cache_ref = firestore_client.collection("response_cache").document(str(prompt_hash))
    cache_ref.set({
        "prompt": prompt,
        "response": response,
        "timestamp": datetime.utcnow().isoformat()
    })
```

#### **Uso del Caching**
```python
async def generate_response_with_cache(
    message: str,
    session_context: list,
    knowledge_context: dict
) -> str:
    """Genera una respuesta usando caching."""
    prompt = build_prompt(message, session_context, knowledge_context)
    
    # Buscar en caché
    cached_response = await get_cached_response(prompt)
    if cached_response:
        return cached_response
    
    # Llamar al LLM si no está en caché
    response = await call_mistral_api(prompt)
    if response:
        await cache_response(prompt, response)
    
    return response or "Lo siento, no pude generar una respuesta."
```

### **5.2. Limitar Tokens**
**Problema**: Respuestas largas aumentan el costo de tokens.

**Solución**: Limitar el número de tokens en la respuesta.

#### **Configuración en Mistral/OpenRouter**
```python
payload = {
    "model": "mistral-tiny",
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 200  # Límites a 200 tokens (~150 palabras)
}
```

#### **Configuración en Gemini**
```python
payload = {
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {
        "maxOutputTokens": 200
    }
}
```

### **5.3. Usar Modelos Más Económicos**
| **Modelo**          | **Costo (Input + Output)** | **Recomendación**                     |
|---------------------|----------------------------|---------------------------------------|
| `mistral-tiny`      | ~$0.00000075/token          | ✅ Mejor opción para este proyecto.   |
| `mistral-small`     | ~$0.0000032/token          | Usar si se necesita más precisión.    |
| `gemini-1.0-pro`    | ~$0.000021/token           | ❌ Evitar (muy caro).                  |

### **5.4. Monitorear Uso de Tokens**
**Implementación**:
```python
from google.cloud import firestore

firestore_client = firestore.Client()

async def log_token_usage(model: str, input_tokens: int, output_tokens: int) -> None:
    """Registra el uso de tokens para monitoreo."""
    log_ref = firestore_client.collection("token_usage").document()
    log_ref.set({
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "timestamp": datetime.utcnow().isoformat(),
        "cost": (input_tokens * 0.00000025) + (output_tokens * 0.0000005)  # Costo en USD
    })
```

**Uso**:
```python
response = await call_mistral_api(prompt)
if response:
    # Suponiendo que la API de Mistral devuelve el número de tokens usados
    input_tokens = response.json()["usage"]["prompt_tokens"]
    output_tokens = response.json()["usage"]["completion_tokens"]
    await log_token_usage("mistral-tiny", input_tokens, output_tokens)
```

---

## 📌 **6. Manejo de Errores**

### **6.1. Errores Comunes y Soluciones**
| **Error**                          | **Causa**                                  | **Solución**                                                                 |
|-----------------------------------|-------------------------------------------|------------------------------------------------------------------------------|
| **API Key inválida**             | API key incorrecta o expirada.            | Verificar la API key en las variables de entorno.                          |
| **Modelo no disponible**          | Modelo no existe o no está habilitado.    | Usar un modelo válido (ej: `mistral-tiny`).                                |
| **Timeout en la API**             | La API tarda demasiado en responder.      | Aumentar el timeout (ej: `timeout=30`).                                    |
| **Cuota agotada**                 | Se agotó el saldo de la API.              | Recargar saldo o usar un modelo más económico.                            |
| **Respuesta vacía**               | El LLM no generó una respuesta.           | Validar el prompt y el contexto.                                            |

### **6.2. Código para Manejo de Errores**
```python
from typing import Optional
import requests

async def safe_call_llm_api(
    prompt: str,
    model: str = "mistral-tiny",
    max_retries: int = 3
) -> Optional[str]:
    """
    Llama al LLM con manejo de errores y reintentos.
    
    Args:
        prompt: Prompt para el LLM.
        model: Modelo a usar.
        max_retries: Número máximo de reintentos.
    
    Returns:
        str: Respuesta del LLM, o None si falla después de reintentos.
    """
    for attempt in range(max_retries):
        try:
            if model.startswith("mistral"):
                return await call_mistral_api(prompt, model)
            elif model.startswith("openrouter"):
                return await call_openrouter_api(prompt, model)
            elif model.startswith("gemini"):
                return await call_gemini_api(prompt, model)
            else:
                print(f"Modelo no soportado: {model}")
                return None
        except requests.exceptions.Timeout:
            print(f"Timeout en intento {attempt + 1}/{max_retries}")
            if attempt == max_retries - 1:
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error en intento {attempt + 1}/{max_retries}: {e}")
            if attempt == max_retries - 1:
                return None
    
    return None
```

---

## 📌 **7. Ejemplo Completo de Integración**

### **7.1. Código del Servicio de LLM (`services/llm.py`)**
```python
from typing import Optional, Dict, List
from utils.config import LLM_MODEL, MISTRAL_API_KEY, OPENROUTER_API_KEY, GEMINI_API_KEY
from utils.logging import logger

async def generate_response(
    message: str,
    session_context: List[Dict],
    knowledge_context: Dict
) -> str:
    """
    Genera una respuesta usando el LLM configurado.
    
    Args:
        message: Mensaje del usuario.
        session_context: Historial de mensajes anteriores.
        knowledge_context: Contexto de la base de conocimiento.
    
    Returns:
        str: Respuesta generada por el LLM.
    """
    try:
        # Construir prompt
        prompt = build_prompt(message, session_context, knowledge_context)
        
        # Buscar en caché
        cached_response = await get_cached_response(prompt)
        if cached_response:
            logger.info("Respuesta obtenida de caché")
            return cached_response
        
        # Llamar al LLM
        response = await safe_call_llm_api(prompt, LLM_MODEL)
        if not response:
            return "Lo siento, no pude generar una respuesta. Por favor, inténtalo de nuevo."
        
        # Guardar en caché
        await cache_response(prompt, response)
        
        return response
        
    except Exception as e:
        logger.error(f"Error generando respuesta: {e}", exc_info=True)
        return "Lo siento, hubo un error. Por favor, contacta a soporte técnico."
```

### **7.2. Configuración de Variables de Entorno (`.env`)**
```ini
# --- Twilio ---
TWILIO_ACCOUNT_SID=tu_account_sid
TWILIO_AUTH_TOKEN=tu_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# --- LLM ---
# Opción 1: Mistral API
LLM_MODEL=mistral-tiny
MISTRAL_API_KEY=tu_mistral_api_key

# Opción 2: OpenRouter API
# LLM_MODEL=mistralai/mistral-tiny
# OPENROUTER_API_KEY=tu_openrouter_api_key

# Opción 3: Gemini API
# LLM_MODEL=gemini-1.0-pro
# GEMINI_API_KEY=tu_gemini_api_key

# --- Firestore ---
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# --- Logging ---
LOG_LEVEL=INFO
```

---

## 📌 **8. Pruebas de la Integración**

### **8.1. Pruebas Unitarias**
```python
import pytest
from services.llm import build_prompt, call_mistral_api

def test_build_prompt():
    """Prueba que el prompt se construye correctamente."""
    message = "¿Cuánto cuesta el Producto 1?"
    session_context = [{"role": "user", "content": "Hola"}]
    knowledge_context = {
        "company": {"name": "Mi Empresa"},
        "products": [{"name": "Producto 1", "price": 100}],
        "faq": []
    }
    
    prompt = build_prompt(message, session_context, knowledge_context)
    
    assert "Mi Empresa" in prompt
    assert "Producto 1" in prompt
    assert "¿Cuánto cuesta el Producto 1?" in prompt
    assert "user: Hola" in prompt

@pytest.mark.asyncio
async def test_call_mistral_api():
    """Prueba la llamada a Mistral API (mock)."""
    # Mock de requests.post
    import requests_mock
    
    with requests_mock.Mocker() as m:
        m.post(
            "https://api.mistral.ai/v1/chat/completions",
            json={
                "choices": [{"message": {"content": "Respuesta de prueba"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5}
            },
            status_code=200
        )
        
        response = await call_mistral_api("Prueba", "mistral-tiny")
        assert response == "Respuesta de prueba"
```

### **8.2. Pruebas de Integración**
1. **Probar con un mensaje real**:
   - Envía un mensaje de WhatsApp al número de Twilio.
   - Verifica que el agente responda correctamente.

2. **Probar con preguntas frecuentes**:
   - Pregunta: "¿Cuál es el precio del Producto 1?"
   - Respuesta esperada: "El precio del **Producto 1** es **$100**."

3. **Probar con preguntas abiertas**:
   - Pregunta: "¿Qué productos tienen para el hogar?"
   - Respuesta esperada: Lista de productos para el hogar.

4. **Probar con contexto**:
   - Mensaje 1: "¿Qué productos tienen?"
   - Mensaje 2: "¿Cuánto cuesta el primero?"
   - Respuesta esperada: Precio del primer producto mencionado.

---

## 📌 **9. Monitoreo y Métricas**

### **9.1. Métricas Clave**
| **Métrica**               | **Herramienta**          | **Objetivo**               | **Cómo Medir**                          |
|---------------------------|--------------------------|----------------------------|------------------------------------------|
| Tiempo de respuesta       | Cloud Monitoring         | < 5 segundos               | Métrica `latency` en Cloud Run.          |
| Número de mensajes        | Cloud Logging            | ~100 usuarios/día          | Contar logs con `message_received`.      |
| Tokens usados (LLM)       | Logs personalizados      | ≤ 10K tokens/día           | Sumar `input_tokens` + `output_tokens`.   |
| Costo mensual             | GCP Billing Dashboard     | ≤ $50                      | Revisar facturación en GCP Console.      |
| Errores del LLM           | Cloud Logging            | 0 errores críticos         | Contar logs con `level=ERROR`.           |

### **9.2. Dashboard de Monitoreo**
Puedes crear un **dashboard en Cloud Monitoring** con las siguientes métricas:
1. **Latencia de Cloud Run**: Tiempo de respuesta del backend.
2. **Número de solicitudes**: Mensajes procesados por día.
3. **Uso de Firestore**: Lecturas/escrituras por día.
4. **Logs de errores**: Número de errores por día.

**Ejemplo de consulta para Cloud Logging**:
```sql
# Contar mensajes recibidos por día
resource.type="cloud_run_revision"
resource.labels.service_name="whatsapp-agent-backend"
jsonPayload.message="Mensaje recibido"
| count by timestamp(date)
```

---

## 📌 **10. Resumen de Buenas Prácticas**

### **✅ Hacer**
1. **Usar Mistral API** (más económico que Gemini).
2. **Limitar tokens** a 200 por respuesta.
3. **Implementar caching** para preguntas frecuentes.
4. **Monitorear uso de tokens** para evitar sorpresas en costos.
5. **Validar el prompt** antes de llamarlo (evitar prompts vacíos o mal formateados).
6. **Manejar errores** con reintentos y mensajes amigables.

### **❌ Evitar**
1. **Usar modelos caros** (ej: `gemini-1.5-pro`).
2. **No limitar tokens** (puede generar respuestas largas y costosas).
3. **No usar caching** (aumenta costos innecesariamente).
4. **Ignorar errores** (puede llevar a experiencias malas para el usuario).
5. **Prompts ambiguos** (el LLM puede generar respuestas genéricas).

---

## 📅 **Historial de Cambios**
| **Versión** | **Fecha**       | **Autor**               | **Cambios**                                  |
|-------------|-----------------|-------------------------|---------------------------------------------|
| 1.0         | 2024-10-01      | Equipo de Desarrollo    | Versión inicial con integración completa.  |

---

## 🚀 **Próximos Pasos**
1. **Configurar API Keys** para Mistral/OpenRouter/Gemini.
2. **Implementar el cliente de LLM** (`services/llm.py`).
3. **Probar el prompt** con ejemplos reales.
4. **Integrar con el backend** (webhook de WhatsApp).
5. **Monitorear costos** y ajustar según sea necesario.

**¿Listo para integrar el LLM con el agente?** ✅
