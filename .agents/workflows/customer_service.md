# 🛒 Flujo de Servicio al Cliente y Ventas

## 🎯 **Objetivo**
Este documento describe el **flujo completo de servicio al cliente y ventas** del agente de WhatsApp, incluyendo:
1. **Tipos de interacciones** (consultas, ventas, soporte).
2. **Flujo de conversación** (desde el saludo hasta el cierre).
3. **Manejo de intenciones** (detección de qué quiere el cliente).
4. **Respuestas personalizadas** (según el tipo de producto o servicio).
5. **Escalamiento a humanos** (cuándo y cómo derivar a un agente).
6. **Ejemplos de conversaciones reales**.

---

## 📌 **1. Tipos de Interacciones**

El agente debe manejar los siguientes tipos de interacciones:

| **Tipo**               | **Descripción**                                                                 | **Ejemplo de Mensaje**                     | **Respuesta Esperada**                          |
|------------------------|-------------------------------------------------------------------------------|--------------------------------------------|-------------------------------------------------|
| **Saludo**             | El cliente inicia la conversación.                                           | "Hola", "Buenos días"                     | "¡Hola! ¿En qué puedo ayudarte hoy?"            |
| **Consulta de productos** | El cliente pregunta sobre productos o servicios.                          | "¿Qué productos tienen?"                  | Lista de productos con descripciones.         |
| **Consulta de precios** | El cliente pregunta el precio de un producto.                               | "¿Cuánto cuesta el Producto 1?"           | "El precio del **Producto 1** es **$100**."     |
| **Consulta de características** | El cliente pregunta sobre características de un producto.       | "¿Qué incluye el Producto 2?"              | Descripción detallada del producto.            |
| **Consulta de disponibilidad** | El cliente pregunta si un producto está disponible.               | "¿Tienen el Producto 1 en stock?"          | "Sí, el **Producto 1** está disponible."      |
| **Consulta de garantía** | El cliente pregunta sobre garantías o políticas.                         | "¿Ofrecen garantía?"                      | "Sí, todos nuestros productos tienen garantía de 1 año." |
| **Consulta de envíos**  | El cliente pregunta sobre tiempos o costos de envío.                       | "¿Cuánto cuesta el envío?"                | "El envío es gratuito para compras mayores a $200." |
| **Intención de compra** | El cliente expresa interés en comprar.                                    | "Quiero comprar el Producto 1"            | "¡Excelente! ¿Necesitas ayuda con el proceso?" |
| **Queja o reclamo**    | El cliente reporta un problema.                                              | "El Producto 1 no funciona"                | "Lamentamos el inconveniente. ¿Puedes describir el problema?" |
| **Despedida**          | El cliente cierra la conversación.                                         | "Gracias", "Adiós"                        | "¡Gracias por contactarnos! Que tengas un buen día." |
| **Fuera de contexto**   | El cliente pregunta algo no relacionado con la empresa.                     | "¿Qué hora es?"                           | "No tengo esa información. ¿En qué más puedo ayudarte?" |

---

## 📌 **2. Flujo de Conversación**

### **2.1. Diagrama de Flujo**
```mermaid
graph TD
    A[Cliente envía mensaje] --> B{¿Es un saludo?}
    B -->|Sí| C[Responder saludo]
    B -->|No| D{¿Es una consulta?}
    D -->|Sí| E[Identificar tipo de consulta]
    E --> F[Buscar en base de conocimiento]
    F --> G{¿Encontró respuesta?}
    G -->|Sí| H[Responder con información]
    G -->|No| I[Generar respuesta con LLM]
    I --> H
    D -->|No| J{¿Es una intención de compra?}
    J -->|Sí| K[Iniciar flujo de ventas]
    J -->|No| L{¿Es una queja?}
    L -->|Sí| M[Iniciar flujo de soporte]
    L -->|No| N[Responder: "No entiendo tu solicitud"]
    
    H --> O[Preguntar: "¿Necesitas algo más?"]
    K --> O
    M --> O
    O --> P{¿Cliente responde?}
    P -->|Sí| A
    P -->|No| Q[Cerrar conversación]
```

### **2.2. Estados de la Conversación**
| **Estado**               | **Descripción**                                                                 | **Acciones del Agente**                          |
|--------------------------|-------------------------------------------------------------------------------|-------------------------------------------------|
| **Inicial**              | El cliente envía el primer mensaje.                                          | Saludar y preguntar cómo ayudar.                |
| **Consulta**             | El cliente hace una pregunta sobre productos, precios, etc.                 | Buscar respuesta en base de conocimiento o LLM. |
| **Ventas**               | El cliente expresa interés en comprar.                                        | Proporcionar información de compra.             |
| **Soporte**              | El cliente reporta un problema.                                                | Solicitar más detalles y ofrecer soluciones.     |
| **Cierre**               | El cliente indica que no necesita más ayuda.                                  | Despedirse y agradecer.                         |

---

## 📌 **3. Manejo de Intenciones**

### **3.1. Detección de Intención**
El agente debe **identificar la intención** del cliente para responder de manera adecuada. Esto se puede hacer de dos formas:

1. **Basado en palabras clave** (rápido y económico):
   - Usar **reglas simples** para detectar intenciones comunes.
   - Ejemplo: Si el mensaje contiene "precio", "cuánto cuesta", → **Intención: Consulta de precios**.

2. **Usando el LLM** (más preciso pero más costoso):
   - Pedirle al LLM que **clasifique la intención** del mensaje.
   - Ejemplo: "Clasifica la siguiente pregunta en una de estas categorías: [saludo, consulta_productos, consulta_precios, intención_compra, queja, otro]"

**Recomendación**: Usar **palabras clave** para intenciones comunes y el **LLM** solo para mensajes ambiguos.

### **3.2. Implementación con Palabras Clave**
```python
from typing import Optional

def detect_intention(message: str) -> str:
    """
    Detecta la intención del mensaje usando palabras clave.
    
    Args:
        message: Mensaje del cliente.
    
    Returns:
        str: Intención detectada (ej: "consulta_precios").
    """
    message_lower = message.lower()
    
    # Palabras clave para cada intención
    intention_keywords = {
        "saludo": ["hola", "buenos días", "buenas tardes", "buenas noches", "hey"],
        "despedida": ["gracias", "adiós", "hasta luego", "chao", "bye"],
        "consulta_productos": ["qué productos", "qué tienen", "catálogo", "productos", "servicios"],
        "consulta_precios": ["precio", "cuánto cuesta", "cuánto vale", "¿cuánto?", "costo"],
        "consulta_caracteristicas": ["qué incluye", "características", "especificaciones", "detalles"],
        "consulta_disponibilidad": ["disponible", "stock", "hay", "tienen"],
        "consulta_garantia": ["garantía", "garantia", "devolución", "cambios"],
        "consulta_envio": ["envío", "envio", "entrega", "envían", "envian"],
        "intencion_compra": ["comprar", "quiero", "me interesa", "adquirir", "pedir"],
        "queja": ["problema", "no funciona", "defecto", "reclamo", "queja"],
        "otro": []
    }
    
    for intention, keywords in intention_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            return intention
    
    return "otro"
```

### **3.3. Implementación con LLM**
```python
async def detect_intention_with_llm(message: str) -> str:
    """
    Detecta la intención del mensaje usando el LLM.
    
    Args:
        message: Mensaje del cliente.
    
    Returns:
        str: Intención detectada.
    """
    prompt = f"""
    Clasifica el siguiente mensaje en una de estas categorías:
    - saludo
    - despedida
    - consulta_productos
    - consulta_precios
    - consulta_caracteristicas
    - consulta_disponibilidad
    - consulta_garantia
    - consulta_envio
    - intencion_compra
    - queja
    - otro
    
    Mensaje: "{message}"
    
    Responde **solo con el nombre de la categoría** (sin explicaciones).
    """
    
    response = await call_mistral_api(prompt, max_tokens=20)
    return response.strip().lower() if response else "otro"
```

### **3.4. Flujo de Decisión**
```python
async def handle_message(message: str, sender: str) -> str:
    """
    Maneja un mensaje del cliente según su intención.
    
    Args:
        message: Mensaje del cliente.
        sender: Número del cliente.
    
    Returns:
        str: Respuesta del agente.
    """
    # 1. Detectar intención
    intention = detect_intention(message)
    
    # 2. Manejar según la intención
    if intention == "saludo":
        return await handle_greeting(sender)
    elif intention == "despedida":
        return await handle_farewell(sender)
    elif intention in ["consulta_productos", "consulta_precios", "consulta_caracteristicas", 
                       "consulta_disponibilidad", "consulta_garantia", "consulta_envio"]:
        return await handle_query(message, intention, sender)
    elif intention == "intencion_compra":
        return await handle_purchase_intent(message, sender)
    elif intention == "queja":
        return await handle_complaint(message, sender)
    else:
        return await handle_other(message, sender)
```

---

## 📌 **4. Respuestas Personalizadas**

### **4.1. Respuestas para Consultas de Productos**
**Ejemplo de base de conocimiento**:
```json
{
  "products": [
    {
      "id": "producto_1",
      "name": "Producto 1",
      "description": "Un producto revolucionario para el hogar.",
      "price": 100,
      "features": ["Duradero", "Fácil de usar", "Ecológico"],
      "stock": true,
      "category": "hogar"
    },
    {
      "id": "producto_2",
      "name": "Producto 2",
      "description": "La solución definitiva para tus necesidades.",
      "price": 150,
      "features": ["Rápido", "Eficiente", "Garantía de 1 año"],
      "stock": true,
      "category": "oficina"
    }
  ]
}
```

**Respuestas**:
| **Pregunta**                          | **Respuesta**                                                                 |
|--------------------------------------|------------------------------------------------------------------------------|
| "¿Qué productos tienen?"            | "Tenemos los siguientes productos:\n- **Producto 1**: Un producto revolucionario para el hogar. **Precio: $100**.\n- **Producto 2**: La solución definitiva para tus necesidades. **Precio: $150**." |
| "¿Qué productos tienen para el hogar?" | "Para el hogar, recomendamos el **Producto 1**: Un producto revolucionario, duradero y ecológico. **Precio: $100**." |
| "¿Cuál es el más barato?"            | "El producto más económico es el **Producto 1** con un precio de **$100**." |

**Implementación**:
```python
async def handle_query(message: str, intention: str, sender: str) -> str:
    """Maneja consultas sobre productos, precios, etc."""
    knowledge_context = await get_knowledge_context()
    products = knowledge_context.get("products", [])
    
    if intention == "consulta_productos":
        if "hogar" in message.lower():
            home_products = [p for p in products if p.get("category") == "hogar"]
            if home_products:
                return format_products(home_products)
        return format_products(products)
    
    elif intention == "consulta_precios":
        # Extraer nombre del producto del mensaje
        product_name = extract_product_name(message)
        if product_name:
            product = next((p for p in products if p["name"].lower() == product_name.lower()), None)
            if product:
                return f"El precio del **{product['name']}** es **${product['price']}**."
        return f"Los precios de nuestros productos son:\n{format_prices(products)}"
    
    elif intention == "consulta_caracteristicas":
        product_name = extract_product_name(message)
        if product_name:
            product = next((p for p in products if p["name"].lower() == product_name.lower()), None)
            if product:
                features = ", ".join(product.get("features", []))
                return f"El **{product['name']}** incluye: {features}."
        return "¿Podrías especificar de qué producto quieres saber las características?"
    
    elif intention == "consulta_disponibilidad":
        product_name = extract_product_name(message)
        if product_name:
            product = next((p for p in products if p["name"].lower() == product_name.lower()), None)
            if product:
                stock = "disponible" if product.get("stock", False) else "no disponible"
                return f"El **{product['name']}** está **{stock}**."
        return "Todos nuestros productos están disponibles. ¿Te interesa alguno en particular?"
    
    else:
        return await generate_response_with_llm(message, sender)

def extract_product_name(message: str) -> Optional[str]:
    """Extrae el nombre de un producto del mensaje."""
    knowledge_context = await get_knowledge_context()
    product_names = [p["name"].lower() for p in knowledge_context.get("products", [])]
    
    message_lower = message.lower()
    for name in product_names:
        if name in message_lower:
            return name
    return None

def format_products(products: list) -> str:
    """Formatea una lista de productos para respuesta."""
    return "\n".join([
        f"- **{p['name']}**: {p['description']} (Precio: ${p['price']})"
        for p in products
    ])

def format_prices(products: list) -> str:
    """Formatea una lista de precios."""
    return "\n".join([f"- **{p['name']}**: ${p['price']}" for p in products])
```

---

### **4.2. Respuestas para Intención de Compra**
**Flujo de ventas**:
1. **Confirmar interés**: "¡Excelente! El **Producto 1** es una gran elección."
2. **Proporcionar detalles**: "Incluye [características] y tiene un precio de **$100**."
3. **Preguntar por dudas**: "¿Tienes alguna pregunta antes de proceder?"
4. **Derivar a humano**: "Para completar la compra, un agente te contactará en breve."

**Implementación**:
```python
async def handle_purchase_intent(message: str, sender: str) -> str:
    """Maneja intenciones de compra."""
    # Extraer nombre del producto
    product_name = extract_product_name(message)
    knowledge_context = await get_knowledge_context()
    products = knowledge_context.get("products", [])
    
    if product_name:
        product = next((p for p in products if p["name"].lower() == product_name.lower()), None)
        if product:
            features = ", ".join(product.get("features", []))
            return (
                f"¡Excelente elección! El **{product['name']}** es perfecto para ti.\n"
                f"**Descripción**: {product['description']}\n"
                f"**Características**: {features}\n"
                f"**Precio**: ${product['price']}\n\n"
                f"¿Tienes alguna pregunta antes de proceder con la compra?"
            )
    
    return (
        "¡Genial! ¿Qué producto te interesa comprar?\n"
        f"Tenemos disponibles:\n{format_products(products)}"
    )
```

---

### **4.3. Respuestas para Quejas o Soporte**
**Flujo de soporte**:
1. **Agradecer por el reporte**: "Lamentamos el inconveniente. Gracias por reportarlo."
2. **Solicitar detalles**: "¿Podrías describir el problema con más detalle?"
3. **Ofrecer soluciones**: "Prueba reiniciando el dispositivo. Si el problema persiste, te derivaremos a soporte."
4. **Derivar a humano**: "Un agente de soporte te contactará en breve para ayudarte."

**Implementación**:
```python
async def handle_complaint(message: str, sender: str) -> str:
    """Maneja quejas o problemas reportados."""
    # Guardar la queja en Firestore para seguimiento
    await save_complaint(sender, message)
    
    return (
        "Lamentamos el inconveniente. ¿Podrías describir el problema con más detalle?\n"
        "Por ejemplo:\n"
        "- ¿Qué producto o servicio está fallando?\n"
        "- ¿Qué error específico estás experimentando?\n"
        "- ¿Cuándo comenzó el problema?\n\n"
        "Un agente revisará tu caso y te contactará pronto."
    )

async def save_complaint(sender: str, message: str) -> None:
    """Guarda una queja en Firestore para seguimiento."""
    complaints_ref = firestore_client.collection("complaints")
    complaints_ref.add({
        "sender": sender,
        "message": message,
        "status": "pending",
        "timestamp": datetime.utcnow().isoformat()
    })
```

---

### **4.4. Respuestas para Otros Casos**
**Ejemplos**:
- **Mensaje fuera de contexto**: "No tengo esa información. ¿En qué más puedo ayudarte?"
- **Mensaje vacío**: "¿Podrías repetir tu mensaje? No lo recibí correctamente."
- **Mensaje no entendido**: "No estoy seguro de entender tu solicitud. ¿Podrías reformularla?"

**Implementación**:
```python
async def handle_other(message: str, sender: str) -> str:
    """Maneja mensajes que no encajan en ninguna categoría."""
    # Intentar generar una respuesta con LLM
    response = await generate_response_with_llm(message, sender)
    
    if not response or "no sé" in response.lower():
        return (
            "No tengo esa información. ¿En qué más puedo ayudarte?\n"
            "Puedes preguntarme sobre:\n"
            "- Nuestros productos y servicios\n"
            "- Precios y disponibilidad\n"
            "- Garantías y políticas de devolución"
        )
    
    return response
```

---

## 📌 **5. Escalamiento a Humanos**

### **5.1. ¿Cuándo Escalar?**
El agente debe **derivar a un humano** en los siguientes casos:
1. **No puede responder**: El LLM no tiene suficiente información.
2. **Queja compleja**: El cliente reporta un problema que requiere investigación.
3. **Intención de compra**: El cliente quiere comprar pero necesita ayuda adicional.
4. **Solicitud personalizada**: El cliente pide algo fuera del alcance del agente (ej: cotización personalizada).

### **5.2. Implementación del Escalamiento**

#### **Opción 1: Notificación por Email**
```python
import smtplib
from email.mime.text import MIMEText

async def notify_human_agent(sender: str, message: str, reason: str) -> None:
    """
    Notifica a un agente humano vía email.
    
    Args:
        sender: Número del cliente.
        message: Mensaje del cliente.
        reason: Razón del escalamiento (ej: "queja", "compra").
    """
    # Configuración del email (usar variables de entorno)
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    to_email = os.getenv("SUPPORT_EMAIL", "soporte@empresa.com")
    
    subject = f"[Escalamiento] {reason}: {sender}"
    body = f"""
    Un cliente necesita atención humana.
    
    Número del cliente: {sender}
    Mensaje: {message}
    Razón: {reason}
    
    Por favor, contacta al cliente lo antes posible.
    """
    
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
```

#### **Opción 2: Notificación por Slack**
```python
import requests

async def notify_slack(sender: str, message: str, reason: str) -> None:
    """
    Notifica a un agente humano vía Slack.
    
    Args:
        sender: Número del cliente.
        message: Mensaje del cliente.
        reason: Razón del escalamiento.
    """
    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    payload = {
        "text": f":warning: *Escalamiento de WhatsApp* :warning:",
        "attachments": [
            {
                "color": "#ff0000",
                "fields": [
                    {"title": "Número del cliente", "value": sender, "short": True},
                    {"title": "Razón", "value": reason, "short": True},
                    {"title": "Mensaje", "value": message, "short": False}
                ]
            }
        ]
    }
    
    requests.post(slack_webhook_url, json=payload)
```

#### **Opción 3: Respuesta Automática + Notificación**
```python
async def escalate_to_human(sender: str, message: str, reason: str) -> str:
    """
    Escalar a un humano y notificar al cliente.
    
    Args:
        sender: Número del cliente.
        message: Mensaje del cliente.
        reason: Razón del escalamiento.
    
    Returns:
        str: Respuesta para el cliente.
    """
    # Notificar a humano
    await notify_human_agent(sender, message, reason)
    
    # Responder al cliente
    return (
        "Gracias por tu mensaje. Un agente humano te contactará en breve para ayudarte.\n"
        "Mientras tanto, puedes revisar nuestra información en [enlace a web]."
    )
```

---

## 📌 **6. Ejemplos de Conversaciones Reales**

### **6.1. Ejemplo 1: Consulta de Productos**
```text
Cliente: Hola, ¿qué productos tienen?

Agente: ¡Hola! Tenemos los siguientes productos:
- **Producto 1**: Un producto revolucionario para el hogar. **Precio: $100**.
- **Producto 2**: La solución definitiva para tus necesidades. **Precio: $150**.

¿Te interesa alguno en particular?

Cliente: Sí, ¿qué incluye el Producto 1?

Agente: El **Producto 1** incluye:
- Duradero
- Fácil de usar
- Ecológico

¿Necesitas más información?

Cliente: No, gracias.

Agente: ¡Perfecto! Si tienes más preguntas, no dudes en preguntar. Que tengas un buen día.
```

### **6.2. Ejemplo 2: Intención de Compra**
```text
Cliente: Quiero comprar el Producto 2.

Agente: ¡Excelente elección! El **Producto 2** es perfecto para ti.
**Descripción**: La solución definitiva para tus necesidades.
**Características**: Rápido, Eficiente, Garantía de 1 año
**Precio**: $150

¿Tienes alguna pregunta antes de proceder con la compra?

Cliente: ¿Incluye envío gratuito?

Agente: Sí, el envío es gratuito para compras mayores a $100. El **Producto 2** califica para envío gratuito.

Cliente: Perfecto, quiero comprarlo.

Agente: Para completar tu compra, un agente te contactará en breve para confirmar los detalles y procesar el pago. ¿Necesitas algo más mientras tanto?
```

### **6.3. Ejemplo 3: Queja**
```text
Cliente: Hola, el Producto 1 que compré no funciona.

Agente: Lamentamos el inconveniente. ¿Podrías describir el problema con más detalle?
Por ejemplo:
- ¿Qué error específico estás experimentando?
- ¿Cuándo comenzó el problema?

Un agente revisará tu caso y te contactará pronto.

Cliente: No enciende, lo compré ayer.

Agente: Gracias por los detalles. Hemos notificado a nuestro equipo de soporte. Un agente te contactará en las próximas horas para resolver el problema.
```

### **6.4. Ejemplo 4: Consulta de Precios**
```text
Cliente: ¿Cuánto cuesta el Producto 1?

Agente: El precio del **Producto 1** es **$100**.

Cliente: ¿Y el Producto 2?

Agente: El precio del **Producto 2** es **$150**.

Cliente: Gracias.

Agente: ¡De nada! Si necesitas más información, aquí estoy. Que tengas un buen día.
```

---

## 📌 **7. Personalización por Tipo de Cliente**

### **7.1. Clientes Nuevos vs. Existentes**
- **Clientes nuevos**: Respuestas más detalladas (ej: incluir descripción de la empresa).
- **Clientes existentes**: Respuestas más directas (asumir que ya conocen la empresa).

**Implementación**:
```python
async def get_customer_type(sender: str) -> str:
    """
    Determina si el cliente es nuevo o existente.
    
    Args:
        sender: Número del cliente.
    
    Returns:
        str: "nuevo" o "existente".
    """
    # Buscar en Firestore si el cliente ha interactuado antes
    session_ref = firestore_client.collection("chat_sessions").document(sender)
    session_doc = session_ref.get()
    
    if session_doc.exists:
        return "existente"
    return "nuevo"

async def handle_message(message: str, sender: str) -> str:
    """Maneja un mensaje según el tipo de cliente."""
    customer_type = await get_customer_type(sender)
    
    if customer_type == "nuevo":
        # Para clientes nuevos, incluir más contexto
        knowledge_context = await get_knowledge_context()
        company_info = knowledge_context.get("company", {})
        return (
            f"¡Hola! Bienvenido a **{company_info.get('name', 'nuestra empresa')}**.\n"
            f"{company_info.get('description', '')}\n\n"
            f"¿En qué puedo ayudarte hoy?"
        )
    else:
        # Para clientes existentes, respuesta más directa
        return "¿En qué más puedo ayudarte hoy?"
```

---

## 📌 **8. Manejo de Conversaciones Largas**

### **8.1. Límites de la Conversación**
- **Máximo de mensajes por sesión**: 50 (para evitar costos altos en Firestore).
- **Tiempo máximo de inactividad**: 1 hora (si el cliente no responde, se cierra la sesión).

**Implementación**:
```python
async def save_message(sender: str, role: str, content: str) -> None:
    """Guarda un mensaje en la sesión del cliente."""
    session_ref = firestore_client.collection("chat_sessions").document(sender)
    
    # Obtener sesión actual
    session_doc = session_ref.get()
    messages = session_doc.to_dict().get("messages", []) if session_doc.exists else []
    
    # Limitar a 50 mensajes por sesión
    if len(messages) >= 50:
        messages = messages[-49:]  # Mantener los últimos 49 mensajes
    
    # Agregar nuevo mensaje
    messages.append({
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Actualizar sesión
    session_ref.set({
        "last_updated": datetime.utcnow().isoformat(),
        "messages": messages
    }, merge=True)
    
    # Limpiar sesiones inactivas (más de 1 hora)
    await cleanup_old_sessions()
```

---

## 📌 **9. Resumen de Buenas Prácticas**

### **✅ Hacer**
1. **Detectar intenciones** con palabras clave para preguntas comunes.
2. **Usar el LLM** solo para mensajes ambiguos o complejos.
3. **Mantener contexto** en la conversación (historial de mensajes).
4. **Personalizar respuestas** según el tipo de cliente (nuevo/existente).
5. **Escalar a humanos** cuando el agente no pueda resolver el problema.
6. **Limitar longitud de respuestas** (máximo 200 palabras).
7. **Validar datos** (ej: nombres de productos) antes de responder.

### **❌ Evitar**
1. **Respuestas genéricas** (ej: "No sé", "Consulta con un agente").
2. **Ignorar el contexto** (el LLM debe usar el historial de la conversación).
3. **No validar intenciones** (puede llevar a respuestas incorrectas).
4. **No escalar cuando sea necesario** (puede frustrar al cliente).
5. **Respuestas demasiado largas** (aumenta costos y confunde al cliente).

---

## 📅 **Historial de Cambios**
| **Versión** | **Fecha**       | **Autor**               | **Cambios**                                  |
|-------------|-----------------|-------------------------|---------------------------------------------|
| 1.0         | 2024-10-01      | Equipo de Desarrollo    | Versión inicial con flujos completos.      |

---

## 🚀 **Próximos Pasos**
1. **Implementar la detección de intenciones** (`detect_intention`).
2. **Desarrollar los handlers** para cada tipo de interacción.
3. **Configurar el escalamiento a humanos** (email/Slack).
4. **Probar con conversaciones reales** y ajustar respuestas.

**¿Listo para implementar el flujo de servicio al cliente?** ✅
