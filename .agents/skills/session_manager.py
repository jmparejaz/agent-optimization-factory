# 🗃️ Session Manager - Manejo de Sesiones de Chat
# Este módulo maneja el almacenamiento y recuperación de sesiones de chat en Firestore.

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from google.cloud import firestore
from utils.logging import logger
from utils.config import FIRESTORE_COLLECTION_SESSIONS

# Inicializar cliente de Firestore
firestore_client = firestore.Client()


class SessionManager:
    """
    Clase para manejar sesiones de chat en Firestore.
    
    Cada sesión contiene:
    - Historial de mensajes (role: "user" o "assistant", content: texto).
    - Timestamp de última actualización.
    """
    
    def __init__(self):
        """Inicializa el manejador de sesiones."""
        logger.info("✅ SessionManager inicializado.")
    
    async def get_session_context(
        self,
        sender: str,
        max_messages: int = 10
    ) -> List[Dict[str, str]]:
        """
        Recupera el historial de mensajes de una sesión.
        
        Args:
            sender: Número del cliente (ej: "whatsapp:+521234567890").
            max_messages: Número máximo de mensajes a recuperar.
        
        Returns:
            list: Lista de mensajes anteriores (últimos `max_messages` para contexto).
        """
        try:
            session_ref = firestore_client.collection(FIRESTORE_COLLECTION_SESSIONS).document(sender)
            session_doc = session_ref.get()
            
            if not session_doc.exists:
                return []
            
            messages = session_doc.to_dict().get("messages", [])
            # Retornar últimos `max_messages` mensajes para contexto
            return messages[-max_messages:] if len(messages) > max_messages else messages
            
        except Exception as e:
            logger.error(f"Error al obtener contexto de sesión para {sender}: {e}", exc_info=True)
            return []
    
    async def save_message(
        self,
        sender: str,
        role: str,
        content: str
    ) -> None:
        """
        Guarda un mensaje en la sesión del cliente.
        
        Args:
            sender: Número del cliente.
            role: "user" o "assistant".
            content: Contenido del mensaje.
        """
        try:
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
            
            logger.info(f"Mensaje guardado en sesión de {sender} ({role}): {content[:50]}...")
            
            # Limpiar sesiones inactivas (más de 1 hora)
            await self._cleanup_old_sessions()
            
        except Exception as e:
            logger.error(f"Error al guardar mensaje en sesión: {e}", exc_info=True)
    
    async def _cleanup_old_sessions(self) -> None:
        """
        Elimina sesiones inactivas (más de 1 hora sin actualización).
        """
        try:
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            sessions_ref = firestore_client.collection(FIRESTORE_COLLECTION_SESSIONS)
            
            # Filtrar sesiones no actualizadas en la última hora
            old_sessions = sessions_ref.where("last_updated", "<", one_hour_ago.isoformat())
            
            deleted_count = 0
            for doc in old_sessions.stream():
                doc.reference.delete()
                deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"Se eliminaron {deleted_count} sesiones inactivas.")
                
        except Exception as e:
            logger.error(f"Error al limpiar sesiones antiguas: {e}", exc_info=True)
    
    async def get_session(self, sender: str) -> Optional[Dict]:
        """
        Obtiene toda la información de una sesión.
        
        Args:
            sender: Número del cliente.
        
        Returns:
            dict: Información de la sesión, o None si no existe.
        """
        try:
            session_ref = firestore_client.collection(FIRESTORE_COLLECTION_SESSIONS).document(sender)
            session_doc = session_ref.get()
            
            if session_doc.exists:
                return session_doc.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Error al obtener sesión de {sender}: {e}", exc_info=True)
            return None
    
    async def delete_session(self, sender: str) -> bool:
        """
        Elimina una sesión.
        
        Args:
            sender: Número del cliente.
        
        Returns:
            bool: True si la sesión fue eliminada, False de lo contrario.
        """
        try:
            session_ref = firestore_client.collection(FIRESTORE_COLLECTION_SESSIONS).document(sender)
            session_ref.delete()
            logger.info(f"Sesión eliminada para {sender}.")
            return True
            
        except Exception as e:
            logger.error(f"Error al eliminar sesión de {sender}: {e}", exc_info=True)
            return False
    
    async def get_active_sessions(self) -> List[Dict]:
        """
        Obtiene todas las sesiones activas (actualizadas en la última hora).
        
        Returns:
            list: Lista de sesiones activas.
        """
        try:
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            sessions_ref = firestore_client.collection(FIRESTORE_COLLECTION_SESSIONS)
            
            active_sessions = sessions_ref.where("last_updated", ">=", one_hour_ago.isoformat())
            return [doc.to_dict() for doc in active_sessions.stream()]
            
        except Exception as e:
            logger.error(f"Error al obtener sesiones activas: {e}", exc_info=True)
            return []


# Instancia global del manejador de sesiones
session_manager = SessionManager()
