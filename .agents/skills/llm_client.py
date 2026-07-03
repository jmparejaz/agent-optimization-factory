# 🤖 LLM Client - Integración con Mistral/OpenRouter/Gemini
# Este módulo maneja la integración con los modelos de lenguaje (LLM).

import os
import hashlib
import requests
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from google.cloud import firestore
from utils.logging import logger
from utils.config import (
    LLM_MODEL,
    MISTRAL_API_KEY,
    OPENROUTER_API_KEY,
    GEMINI_API_KEY,
    FIRESTORE_COLLECTION_SESSIONS
)

# Inicializar cliente de Firestore para caching
firestore_client = firestore.Client()


class LLMClient:
    """
    Cliente para interactuar con modelos de lenguaje (LLM).
    Soporta Mistral API, OpenRouter API y Gemini API.
    
    Atributos:
        model: Modelo de LLM a usar (ej: "mistral-tiny").
        api_key: API key para el servicio de LLM.
        api_url: URL base de la API del LLM.
    """
    
    def __init__(self, model: Optional[str] = None):
        """
        Inicializa el cliente de LLM.
        
        Args:
            model: Modelo de LLM a usar. Si es None, usa LLM_MODEL de config.
        """
        self.model = model or LLM_MODEL
        self.api_key = self._get_api_key()
        self.api_url = self._get_api_url()
        
        if not self.api_key:
            logger.error(f"No se encontró API key para el modelo {self.model}")
        else:
            logger.info(f"✅ LLMClient inicializado con modelo: {self.model}")
    
    def _get_api_key(self) -> Optional[str]:
        """Obtiene la API key según el modelo."""
        if self.model.startswith("mistral"):
            return MISTRAL_API_KEY
        elif self.model.startswith("openrouter"):
            return OPENROUTER_API_KEY
        elif self.model.startswith("gemini"):
            return GEMINI_API_KEY
        else:
            return None
    
    def _get_api_url(self) -> str:
        """Obtiene la URL de la API según el modelo."""
        if self.model.startswith("mistral"):
            return "https://api.mistral.ai/v1/chat/completions"
        elif self.model.startswith("openrouter"):
            return "https://openrouter.ai/api/v1/chat/completions"
        elif self.model.startswith("gemini"):
            return "https://generativelanguage.googleapis.com/v1beta/models"
        else:
            return ""
    
    def build_prompt(
        self,
        message: str,
        session_context: List[Dict[str, str]],
        knowledge_context: Dict[str, Any]
    ) -> str:
        """
        Construye el prompt para el LLM con contexto.
        
        Args:
            message: Mensaje actual del usuario.
            session_context: Historial de mensajes anteriores.
            knowledge_context: Contexto de la base de conocimiento.
        
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
    
    async def generate_response(
        self,
        message: str,
        session_context: List[Dict[str, str]],
        knowledge_context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Genera una respuesta usando el LLM.
        
        Args:
            message: Mensaje del usuario.
            session_context: Historial de mensajes anteriores.
            knowledge_context: Contexto de la base de conocimiento.
        
        Returns:
            str: Respuesta generada por el LLM, o None si hay error.
        """
        try:
            # Construir prompt
            prompt = self.build_prompt(message, session_context, knowledge_context)
            
            # Buscar en caché
            cached_response = await self._get_cached_response(prompt)
            if cached_response:
                logger.info("Respuesta obtenida de caché")
                return cached_response
            
            # Llamar al LLM
            response = await self._call_llm_api(prompt)
            if not response:
                return None
            
            # Guardar en caché
            await self._cache_response(prompt, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generando respuesta con LLM: {e}", exc_info=True)
            return None
    
    async def _call_llm_api(self, prompt: str) -> Optional[str]:
        """
        Llama a la API del LLM según el modelo configurado.
        
        Args:
            prompt: Prompt para el LLM.
        
        Returns:
            str: Respuesta del LLM, o None si hay error.
        """
        if self.model.startswith("mistral"):
            return await self._call_mistral_api(prompt)
        elif self.model.startswith("openrouter"):
            return await self._call_openrouter_api(prompt)
        elif self.model.startswith("gemini"):
            return await self._call_gemini_api(prompt)
        else:
            logger.error(f"Modelo no soportado: {self.model}")
            return None
    
    async def _call_mistral_api(self, prompt: str) -> Optional[str]:
        """Llama a la API de Mistral."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 200
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            # Guardar uso de tokens (opcional)
            usage = response.json().get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            await self._log_token_usage("mistral", input_tokens, output_tokens)
            
            return response.json()["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error llamando a Mistral API: {e}")
            return None
    
    async def _call_openrouter_api(self, prompt: str) -> Optional[str]:
        """Llama a la API de OpenRouter."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 200
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            # Guardar uso de tokens (opcional)
            usage = response.json().get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            await self._log_token_usage("openrouter", input_tokens, output_tokens)
            
            return response.json()["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error llamando a OpenRouter API: {e}")
            return None
    
    async def _call_gemini_api(self, prompt: str) -> Optional[str]:
        """Llama a la API de Gemini."""
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 200
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/{self.model}:generateContent?key={self.api_key}",
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            
            # Guardar uso de tokens (opcional)
            usage = response.json().get("usageMetadata", {})
            input_tokens = usage.get("promptTokenCount", 0)
            output_tokens = usage.get("candidatesTokenCount", 0)
            await self._log_token_usage("gemini", input_tokens, output_tokens)
            
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error llamando a Gemini API: {e}")
            return None
    
    async def _get_cached_response(self, prompt: str) -> Optional[str]:
        """
        Busca una respuesta en caché para el prompt dado.
        
        Args:
            prompt: Prompt completo.
        
        Returns:
            str: Respuesta en caché, o None si no existe o está expirada.
        """
        try:
            # Usar hash del prompt para evitar problemas con caracteres especiales
            prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
            cache_ref = firestore_client.collection("response_cache").document(prompt_hash)
            cache_doc = cache_ref.get()
            
            if cache_doc.exists:
                cache_data = cache_doc.to_dict()
                timestamp = cache_data.get("timestamp")
                
                # Verificar si la caché está vigente (menos de 1 hora)
                if timestamp:
                    cache_time = datetime.fromisoformat(timestamp)
                    if datetime.utcnow() - cache_time < timedelta(hours=1):
                        logger.info("Respuesta obtenida de caché")
                        return cache_data.get("response")
            
            return None
            
        except Exception as e:
            logger.error(f"Error al buscar en caché: {e}")
            return None
    
    async def _cache_response(self, prompt: str, response: str) -> None:
        """
        Guarda una respuesta en caché.
        
        Args:
            prompt: Prompt completo.
            response: Respuesta generada por el LLM.
        """
        try:
            prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
            cache_ref = firestore_client.collection("response_cache").document(prompt_hash)
            cache_ref.set({
                "prompt": prompt,
                "response": response,
                "timestamp": datetime.utcnow().isoformat(),
                "model": self.model
            })
            logger.info("Respuesta guardada en caché")
            
        except Exception as e:
            logger.error(f"Error al guardar en caché: {e}")
    
    async def _log_token_usage(self, model: str, input_tokens: int, output_tokens: int) -> None:
        """
        Registra el uso de tokens para monitoreo.
        
        Args:
            model: Modelo de LLM usado.
            input_tokens: Tokens de entrada usados.
            output_tokens: Tokens de salida usados.
        """
        try:
            log_ref = firestore_client.collection("token_usage").document()
            total_tokens = input_tokens + output_tokens
            
            # Calcular costo (aproximado)
            if model.startswith("mistral"):
                cost = (input_tokens * 0.00000025) + (output_tokens * 0.0000005)
            elif model.startswith("openrouter"):
                # Depende del modelo, usar un promedio
                cost = (input_tokens + output_tokens) * 0.000001
            elif model.startswith("gemini"):
                cost = (input_tokens * 0.000005) + (output_tokens * 0.000016)
            else:
                cost = 0
            
            log_ref.set({
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "cost": cost,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error al registrar uso de tokens: {e}")


# Instancia global del cliente de LLM
llm_client = LLMClient()
