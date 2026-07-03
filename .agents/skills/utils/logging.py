# 📝 Logging - Configuración de Logs
# Este módulo configura el sistema de logging para el agente de WhatsApp.

import logging
from pythonjsonlogger import jsonlogger
import os

# Nivel de logging (por defecto: INFO)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def setup_logging():
    """
    Configura el logging para el agente.
    
    Returns:
        logging.Logger: Logger configurado.
    """
    # Crear logger
    logger = logging.getLogger(__name__)
    
    # Configurar nivel de logging
    level = getattr(logging, LOG_LEVEL, logging.INFO)
    logger.setLevel(level)
    
    # Formateador JSON para Cloud Logging
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s %(funcName)s %(lineno)d"
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# Inicializar logger global
logger = setup_logging()
