# 💬 Response Generator - Generador de Respuestas
# Este módulo genera respuestas contextualizadas para el agente de WhatsApp.

from typing import Optional, Dict, List, Any
from utils.logging import logger
from .llm_client import llm_client
from .knowledge_base import knowledge_base
from .session_manager import session_manager


class ResponseGenerator:
    """
    Generador de respuestas para el agente de WhatsApp.
    
    Usa:
    - Base de conocimiento (empresa, productos, FAQ).
    - Contexto de la sesión (historial de mensajes).
    - LLM (Mistral/OpenRouter/Gemini) para respuestas dinámicas.
    """
    
    def __init__(self):
        """Inicializa el generador de respuestas."""
        logger.info("✅ ResponseGenerator inicializado.")
    
    async def generate_response(
        self,
        sender: str,
        message: str
    ) -> str:
        """
        Genera una respuesta para un mensaje del cliente.
        
        Args:
            sender: Número del cliente (ej: "whatsapp:+521234567890").
            message: Mensaje del cliente.
        
        Returns:
            str: Respuesta generada para el cliente.
        """
        try:
            # 1. Obtener contexto de la sesión
            session_context = await session_manager.get_session_context(sender)
            
            # 2. Obtener contexto de la base de conocimiento
            knowledge_context = await knowledge_base.get_knowledge_context()
            
            # 3. Detectar intención del mensaje
            intention = self._detect_intention(message)
            
            # 4. Generar respuesta según la intención
            if intention == "saludo":
                return await self._handle_greeting(sender, session_context)
            elif intention == "despedida":
                return await self._handle_farewell(sender)
            elif intention in ["consulta_productos", "consulta_precios", "consulta_caracteristicas", 
                               "consulta_disponibilidad", "consulta_garantia", "consulta_envio"]:
                return await self._handle_query(message, intention, knowledge_context)
            elif intention == "intencion_compra":
                return await self._handle_purchase_intent(message, knowledge_context)
            elif intention == "queja":
                return await self._handle_complaint(message, sender)
            else:
                return await self._handle_generic_query(message, session_context, knowledge_context)
                
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}", exc_info=True)
            return "Lo siento, hubo un error al procesar tu solicitud. Por favor, inténtalo de nuevo."
    
    def _detect_intention(self, message: str) -> str:
        """
        Detecta la intención del mensaje usando palabras clave.
        
        Args:
            message: Mensaje del cliente.
        
        Returns:
            str: Intención detectada (ej: "saludo", "consulta_precios", etc.).
        """
        message_lower = message.lower()
        
        # Palabras clave para cada intención
        intention_keywords = {
            "saludo": ["hola", "buenos días", "buenas tardes", "buenas noches", "hey", "hi"],
            "despedida": ["gracias", "adiós", "hasta luego", "chao", "bye", "hasta pronto"],
            "consulta_productos": ["qué productos", "qué tienen", "catálogo", "productos", "servicios", "qué ofrecen"],
            "consulta_precios": ["precio", "cuánto cuesta", "cuánto vale", "¿cuánto?", "costo", "precios"],
            "consulta_caracteristicas": ["qué incluye", "características", "especificaciones", "detalles", "qué tiene"],
            "consulta_disponibilidad": ["disponible", "stock", "hay", "tienen", "existencia"],
            "consulta_garantia": ["garantía", "garantia", "devolución", "cambios", "política"],
            "consulta_envio": ["envío", "envio", "entrega", "envían", "envian", "envío gratuito"],
            "intencion_compra": ["comprar", "quiero", "me interesa", "adquirir", "pedir", "cotización"],
            "queja": ["problema", "no funciona", "defecto", "reclamo", "queja", "error", "fallo"]
        }
        
        for intention, keywords in intention_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return intention
        
        return "otro"
    
    async def _handle_greeting(
        self,
        sender: str,
        session_context: List[Dict[str, str]]
    ) -> str:
        """
        Maneja mensajes de saludo.
        
        Args:
            sender: Número del cliente.
            session_context: Historial de mensajes.
        
        Returns:
            str: Respuesta de saludo.
        """
        # Verificar si es un cliente nuevo o existente
        is_new_customer = len(session_context) == 0
        
        if is_new_customer:
            company_info = await knowledge_base.get_company_info()
            return (
                f"¡Hola! Bienvenido a **{company_info.get('name', 'nuestra empresa')}**.\n\n"
                f"{company_info.get('description', '')}\n\n"
                f"¿En qué puedo ayudarte hoy?"
            )
        else:
            return "¿En qué más puedo ayudarte hoy?"
    
    async def _handle_farewell(self, sender: str) -> str:
        """
        Maneja mensajes de despedida.
        
        Args:
            sender: Número del cliente.
        
        Returns:
            str: Respuesta de despedida.
        """
        return "¡Gracias por contactarnos! Que tengas un excelente día. Si necesitas algo más, no dudes en volver a escribirnos."
    
    async def _handle_query(
        self,
        message: str,
        intention: str,
        knowledge_context: Dict[str, Any]
    ) -> str:
        """
        Maneja consultas sobre productos, precios, etc.
        
        Args:
            message: Mensaje del cliente.
            intention: Intención detectada.
            knowledge_context: Contexto de la base de conocimiento.
        
        Returns:
            str: Respuesta a la consulta.
        """
        products = knowledge_context.get("products", [])
        faq = knowledge_context.get("faq", [])
        
        # 1. Buscar en FAQ
        faq_answer = await knowledge_base.search_in_faq(message)
        if faq_answer:
            return faq_answer
        
        # 2. Manejar según la intención
        if intention == "consulta_productos":
            return self._format_products(products, message)
        elif intention == "consulta_precios":
            return await self._handle_price_query(message, products)
        elif intention == "consulta_caracteristicas":
            return await self._handle_features_query(message, products)
        elif intention == "consulta_disponibilidad":
            return await self._handle_availability_query(message, products)
        elif intention == "consulta_garantia":
            return "Todos nuestros productos incluyen **garantía de 1 año** contra defectos de fábrica."
        elif intention == "consulta_envio":
            return "El **envío es gratuito** para compras mayores a $200. Para compras menores, el costo de envío es de $10."
        else:
            return await self._handle_generic_query(message, [], knowledge_context)
    
    def _format_products(
        self,
        products: List[Dict[str, Any]],
        message: str
    ) -> str:
        """
        Formatea una lista de productos para respuesta.
        
        Args:
            products: Lista de productos.
            message: Mensaje del cliente (para filtrar por categoría).
        
        Returns:
            str: Lista de productos formateada.
        """
        if not products:
            return "Actualmente no tenemos productos disponibles. ¿En qué más puedo ayudarte?"
        
        # Filtrar por categoría si se menciona en el mensaje
        message_lower = message.lower()
        if "hogar" in message_lower:
            products = [p for p in products if p.get("category", "").lower() == "hogar"]
        elif "oficina" in message_lower:
            products = [p for p in products if p.get("category", "").lower() == "oficina"]
        
        if not products:
            return "No tenemos productos en esa categoría. ¿Te interesa ver todos nuestros productos?"
        
        response = "Tenemos los siguientes productos:\n"
        for product in products:
            response += f"- **{product['name']}**: {product['description']} (**${product['price']}**)\n"
        
        return response.strip()
    
    async def _handle_price_query(
        self,
        message: str,
        products: List[Dict[str, Any]]
    ) -> str:
        """
        Maneja consultas de precios.
        
        Args:
            message: Mensaje del cliente.
            products: Lista de productos.
        
        Returns:
            str: Respuesta con el precio.
        """
        # Extraer nombre del producto del mensaje
        product_name = self._extract_product_name(message, products)
        
        if product_name:
            product = next((p for p in products if p["name"].lower() == product_name.lower()), None)
            if product:
                return f"El precio del **{product['name']}** es **${product['price']}**."
        
        # Si no se encontró un producto específico, listar todos los precios
        if products:
            response = "Los precios de nuestros productos son:\n"
            for product in products:
                response += f"- **{product['name']}**: ${product['price']}\n"
            return response.strip()
        
        return "No tenemos información de precios disponible. ¿En qué más puedo ayudarte?"
    
    async def _handle_features_query(
        self,
        message: str,
        products: List[Dict[str, Any]]
    ) -> str:
        """
        Maneja consultas de características.
        
        Args:
            message: Mensaje del cliente.
            products: Lista de productos.
        
        Returns:
            str: Respuesta con las características.
        """
        product_name = self._extract_product_name(message, products)
        
        if product_name:
            product = next((p for p in products if p["name"].lower() == product_name.lower()), None)
            if product:
                features = product.get("features", [])
                if features:
                    return f"El **{product['name']}** incluye: **{', '.join(features)}**."
                else:
                    return f"El **{product['name']}** no tiene características adicionales registradas."
        
        return "¿Podrías especificar de qué producto quieres saber las características?"
    
    async def _handle_availability_query(
        self,
        message: str,
        products: List[Dict[str, Any]]
    ) -> str:
        """
        Maneja consultas de disponibilidad.
        
        Args:
            message: Mensaje del cliente.
            products: Lista de productos.
        
        Returns:
            str: Respuesta sobre disponibilidad.
        """
        product_name = self._extract_product_name(message, products)
        
        if product_name:
            product = next((p for p in products if p["name"].lower() == product_name.lower()), None)
            if product:
                stock = product.get("stock", True)
                stock_status = "disponible" if stock else "no disponible"
                return f"El **{product['name']}** está **{stock_status}**."
        
        return "Todos nuestros productos están disponibles. ¿Te interesa alguno en particular?"
    
    async def _handle_purchase_intent(
        self,
        message: str,
        knowledge_context: Dict[str, Any]
    ) -> str:
        """
        Maneja intenciones de compra.
        
        Args:
            message: Mensaje del cliente.
            knowledge_context: Contexto de la base de conocimiento.
        
        Returns:
            str: Respuesta para guiar la compra.
        """
        products = knowledge_context.get("products", [])
        
        # Extraer nombre del producto del mensaje
        product_name = self._extract_product_name(message, products)
        
        if product_name:
            product = next((p for p in products if p["name"].lower() == product_name.lower()), None)
            if product:
                features = product.get("features", [])
                return (
                    f"¡Excelente elección! El **{product['name']}** es perfecto para ti.\n\n"
                    f"**Descripción**: {product['description']}\n"
                    f"**Características**: {', '.join(features) if features else 'N/A'}\n"
                    f"**Precio**: ${product['price']}\n\n"
                    f"¿Tienes alguna pregunta antes de proceder con la compra?"
                )
        
        # Si no se menciona un producto específico
        return (
            "¡Genial! ¿Qué producto te interesa comprar?\n\n"
            f"Tenemos disponibles:\n{self._format_products(products, '')}"
        )
    
    async def _handle_complaint(
        self,
        message: str,
        sender: str
    ) -> str:
        """
        Maneja quejas o problemas reportados.
        
        Args:
            message: Mensaje del cliente.
            sender: Número del cliente.
        
        Returns:
            str: Respuesta para manejar la queja.
        """
        # Guardar la queja en Firestore para seguimiento
        await self._save_complaint(sender, message)
        
        return (
            "Lamentamos el inconveniente. ¿Podrías describir el problema con más detalle?\n\n"
            "Por ejemplo:\n"
            "- ¿Qué producto o servicio está fallando?\n"
            "- ¿Qué error específico estás experimentando?\n"
            "- ¿Cuándo comenzó el problema?\n\n"
            "Un agente revisará tu caso y te contactará pronto."
        )
    
    async def _handle_generic_query(
        self,
        message: str,
        session_context: List[Dict[str, str]],
        knowledge_context: Dict[str, Any]
    ) -> str:
        """
        Maneja consultas genéricas usando el LLM.
        
        Args:
            message: Mensaje del cliente.
            session_context: Historial de mensajes.
            knowledge_context: Contexto de la base de conocimiento.
        
        Returns:
            str: Respuesta generada por el LLM.
        """
        # Generar respuesta con el LLM
        response = await llm_client.generate_response(
            message=message,
            session_context=session_context,
            knowledge_context=knowledge_context
        )
        
        if not response or "no sé" in response.lower():
            return (
                "No tengo esa información. ¿En qué más puedo ayudarte?\n\n"
                "Puedes preguntarme sobre:\n"
                "- Nuestros productos y servicios\n"
                "- Precios y disponibilidad\n"
                "- Garantías y políticas de devolución"
            )
        
        return response
    
    def _extract_product_name(
        self,
        message: str,
        products: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Extrae el nombre de un producto del mensaje.
        
        Args:
            message: Mensaje del cliente.
            products: Lista de productos.
        
        Returns:
            str: Nombre del producto, o None si no se encuentra.
        """
        message_lower = message.lower()
        product_names = [p["name"].lower() for p in products]
        
        for name in product_names:
            if name in message_lower:
                return name
        
        return None
    
    async def _save_complaint(
        self,
        sender: str,
        message: str
    ) -> None:
        """
        Guarda una queja en Firestore para seguimiento.
        
        Args:
            sender: Número del cliente.
            message: Mensaje del cliente (queja).
        """
        try:
            from google.cloud import firestore
            firestore_client = firestore.Client()
            complaints_ref = firestore_client.collection("complaints")
            complaints_ref.add({
                "sender": sender,
                "message": message,
                "status": "pending",
                "timestamp": datetime.utcnow().isoformat()
            })
            logger.info(f"Queja guardada de {sender}: {message}")
        except Exception as e:
            logger.error(f"Error al guardar queja: {e}", exc_info=True)


# Instancia global del generador de respuestas
response_generator = ResponseGenerator()
