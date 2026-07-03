# 📱 WhatsApp Handler - Manejo de Mensajes de WhatsApp
# Este módulo maneja la recepción y envío de mensajes a través de Twilio WhatsApp API.

import os
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from fastapi import Request
from utils.logging import logger
from utils.config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_NUMBER
)


class WhatsAppHandler:
    """
    Clase para manejar mensajes de WhatsApp a través de Twilio.
    
    Atributos:
        client: Cliente de Twilio para enviar mensajes.
    """
    
    def __init__(self):
        """Inicializa el manejador de WhatsApp."""
        try:
            self.client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            logger.info("✅ Cliente de Twilio inicializado correctamente.")
        except Exception as e:
            logger.error(f"❌ Error inicializando cliente de Twilio: {e}")
            self.client = None
    
    def validate_webhook(self, request: Request) -> bool:
        """
        Valida que la solicitud proviene de Twilio.
        
        Args:
            request: Objeto Request de FastAPI.
        
        Returns:
            bool: True si la solicitud es válida, False de lo contrario.
        """
        # Twilio envía un header 'X-Twilio-Signature' para validar la solicitud
        # Por ahora, omitimos la validación (se recomienda implementarla en producción)
        return True
    
    async def receive_message(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Procesa un mensaje entrante de WhatsApp.
        
        Args:
            request: Objeto Request de FastAPI.
        
        Returns:
            dict: Datos del mensaje (Body, From, MessageSid, etc.), o None si hay error.
        """
        try:
            form_data = await request.form()
            message_data = {
                "Body": form_data.get("Body", "").strip(),
                "From": form_data.get("From", ""),
                "To": form_data.get("To", ""),
                "MessageSid": form_data.get("MessageSid", ""),
                "NumMedia": form_data.get("NumMedia", "0")
            }
            
            logger.info(f"Mensaje recibido de {message_data['From']}: {message_data['Body']}")
            return message_data
            
        except Exception as e:
            logger.error(f"Error procesando mensaje entrante: {e}", exc_info=True)
            return None
    
    def send_message(self, to: str, body: str) -> bool:
        """
        Envía un mensaje de WhatsApp a través de Twilio.
        
        Args:
            to: Número de destino (ej: "whatsapp:+521234567890").
            body: Contenido del mensaje.
        
        Returns:
            bool: True si el mensaje se envió correctamente, False de lo contrario.
        """
        if not self.client:
            logger.error("Cliente de Twilio no inicializado.")
            return False
        
        try:
            message = self.client.messages.create(
                body=body,
                from_=TWILIO_WHATSAPP_NUMBER,
                to=to
            )
            logger.info(f"Mensaje enviado a {to}: {body} (SID: {message.sid})")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando mensaje a {to}: {e}", exc_info=True)
            return False
    
    def generate_twiml_response(self, response_text: str) -> str:
        """
        Genera una respuesta en formato TwiML para Twilio.
        
        Args:
            response_text: Texto de la respuesta.
        
        Returns:
            str: Respuesta en formato TwiML.
        """
        twiml = MessagingResponse()
        twiml.message(response_text)
        return str(twiml)
    
    async def process_webhook(self, request: Request) -> str:
        """
        Procesa una solicitud del webhook de Twilio.
        
        Args:
            request: Objeto Request de FastAPI.
        
        Returns:
            str: Respuesta en formato TwiML.
        """
        # Validar webhook
        if not self.validate_webhook(request):
            logger.warning("Solicitud de webhook no válida.")
            return self.generate_twiml_response("Error: Solicitud no válida.")
        
        # Recibir mensaje
        message_data = await self.receive_message(request)
        if not message_data:
            return self.generate_twiml_response("Error: No se pudo procesar el mensaje.")
        
        # Extraer datos del mensaje
        message_body = message_data.get("Body", "")
        sender = message_data.get("From", "")
        
        # Si no hay mensaje, responder con error
        if not message_body:
            return self.generate_twiml_response("Error: Mensaje vacío.")
        
        # Retornar los datos para que el backend los procese
        # (El procesamiento real se hace en el backend, no aquí)
        return self.generate_twiml_response("Mensaje recibido. Procesando...")


# Instancia global del manejador
whatsapp_handler = WhatsAppHandler()
