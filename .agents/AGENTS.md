# 📌 AGENTS.md - Documentación Maestra del Agente de WhatsApp

## 🎯 **Objetivo del Proyecto**
Desarrollar un **agente de WhatsApp para servicio al cliente y ventas** que:
- Reciba mensajes de clientes nuevos y existentes.
- Responda automáticamente basándose en la **descripción de la empresa y productos**.
- Utilice **Mistral API**, **Gemini API** o **OpenRouter API** para generar respuestas dinámicas.
- esté desplegado en **Google Cloud Platform (GCP)** con un **costo máximo de $50/mes**.
- Soporte **~100 usuarios/día** (escalable).

---

## 📂 **Estructura de Directorios**
```bash
.
├── config.yaml                          # Configuración principal (todos los parámetros aquí)
├── .env.example                         # Ejemplo de variables de entorno
├── .gitignore                           # Archivos ignorados por Git
├── Dockerfile                           # Configuración del contenedor para Cloud Run
├── init_firestore.py                    # Script para inicializar Firestore con datos de config.yaml
├── requirements.txt                     # Dependencias de Python
├── README.md                            # Documentación principal del proyecto
├── src/
│   └── main.py                          # Backend principal (FastAPI)
└── .agents/
    ├── AGENTS.md                        # Este documento
    ├── docs/
    │   ├── requirements.md               # Requisitos detallados
    │   └── gcp_architecture.md           # Arquitectura en GCP (costos, servicios, optimizaciones)
    ├── plans/
    │   ├── master_plan.md                # Plan maestro con fases, tareas y cronograma
    │   └── architecture_diagram.md        # Diagramas de arquitectura (Mermaid)
    ├── workflows/
    │   ├── whatsapp_webhook.md           # Flujo del webhook de WhatsApp (Twilio + Cloud Run)
    │   ├── llm_integration.md            # Integración con Mistral/OpenRouter/Gemini
    │   └── customer_service.md            # Flujo de servicio al cliente (detección de intenciones, respuestas)
    ├── skills/
    │   ├── __init__.py
    │   ├── whatsapp_handler.py           # Manejo de mensajes de WhatsApp (Twilio)
    │   ├── llm_client.py                 # Cliente para Mistral/OpenRouter/Gemini (con caching)
    │   ├── knowledge_base.py             # Acceso a Firestore (empresa, productos, FAQ)
    │   ├── response_generator.py         # Generador de respuestas contextualizadas
    │   ├── session_manager.py            # Manejo de sesiones de chat en Firestore
    │   └── utils/
    │       ├── __init__.py
    │       ├── config.py                 # Configuración cargada desde config.yaml
    │       └── logging.py                # Logging para Cloud Logging
    └── scripts/
        ├── deploy.sh                     # Script para desplegar en Cloud Run (usa config.yaml)
        └── monitor.sh                    # Script para monitorear costos, logs y métricas
```

---

## 🔧 **Tecnologías y Servicios**

### **🌐 Integración con WhatsApp**
- **Proveedor**: [Twilio WhatsApp API](https://www.twilio.com/whatsapp) (recomendado por facilidad).
- **Alternativa**: WhatsApp Business API (Meta) - requiere aprobación.
- **Costo**: ~$0.005 por mensaje (envío + recepción).

### **☁️ Infraestructura en GCP**
| **Servicio**       | **Uso**                          | **Costo Estimado (mensual)** | **Notas**                                  |
|--------------------|----------------------------------|-------------------------------|--------------------------------------------|
| Cloud Run          | Backend (1 vCPU, 2GB RAM)        | ~$20-$30                      | Ejecución bajo demanda.                     |
| Firestore          | Base de conocimiento + sesiones  | ~$5-$10                       | Modo Datastore (económico).                 |
| Pub/Sub            | Cola de mensajes (opcional)      | ~$10                          | Para manejo asíncrono.                      |
| Cloud Storage      | Almacenamiento de logs           | ~$0.02/GB                     | Opcional.                                  |
| Vertex AI          | LLM (Gemini) - alternativa        | ~$5-$10                       | Si no se usa Mistral/OpenRouter.            |
| **Total**          |                                  | **~$45-$50**                  | Ajustable según uso real.                   |

### **🤖 Modelos de Lenguaje (LLM)**
| **API**            | **Modelo Recomendado** | **Costo por Token**       | **Ventajas**                              |
|--------------------|------------------------|----------------------------|--------------------------------------------|
| Mistral API        | `mistral-tiny`         | ~$0.00000025/input, $0.0000005/output | Más económico.                            |
| OpenRouter API     | `mistralai/mistral-tiny` | ~$0.00000025/token       | Acceso a múltiples modelos.                |
| Gemini API         | `gemini-1.0-pro`       | ~$0.000005/input, $0.000016/output | Integración nativa con GCP.               |

---

## 📅 **Fases del Proyecto**

### **🔹 Fase 1: Configuración Inicial (Días 1-2)**
- [x] Crear proyecto en GCP y habilitar servicios.
- [x] Configurar cuenta en Twilio y WhatsApp Sandbox.
- [x] Desarrollar esqueleto del backend (FastAPI + Twilio).
- [x] Probar webhook localmente con ngrok.

**Entregables**:
- Proyecto GCP configurado.
- Cuenta Twilio funcional.
- Código base del backend en `src/main.py`.

---

### **🔹 Fase 2: Base de Conocimiento y LLM (Días 3-4)**
- [x] Crear base de conocimiento en Firestore.
- [x] Integrar Mistral/OpenRouter para generar respuestas.
- [x] Desarrollar lógica de respuestas (combinar base de conocimiento + LLM).

**Entregables**:
- Base de conocimiento en Firestore.
- Integración funcional con Mistral/OpenRouter.
- Respuestas automáticas básicas.

---

### **🔹 Fase 3: Pruebas y Despliegue (Días 5-6)**
- [ ] Desplegar backend en Cloud Run.
- [ ] Configurar webhook de Twilio en producción.
- [ ] Realizar pruebas de usuario con 5-10 clientes reales.
- [ ] Configurar monitoreo (Cloud Logging).

**Entregables**:
- Agente funcional en producción.
- Documentación de despliegue (`./.agents/docs/deployment.md`).
- Pruebas con mensajes reales.

---

### **🔹 Fase 4: Optimización y Documentación (Día 7)**
- [ ] Optimizar uso de LLM (caching, respuestas cortas).
- [ ] Documentar guía de usuario.
- [ ] Documentar guía de despliegue y mantenimiento.
- [ ] Crear plan de escalamiento.

**Entregables**:
- Documentación completa.
- Agente listo para uso real.

---

## 🛠️ **Requisitos Técnicos**

### **Backend (Cloud Run)**
- **Lenguaje**: Python 3.10+ (FastAPI).
- **Dependencias**: Ver `requirements.txt`.
- **Estructura**:
  ```bash
  src/
  └── main.py               # Backend principal (FastAPI)
  ```

### **Base de Conocimiento (Firestore)**
- **Colecciones**:
  - `knowledge_base`: Descripción de la empresa.
  - `products`: Lista de productos y precios.
  - `faq`: Preguntas frecuentes y respuestas.
  - `chat_sessions`: Historial de conversaciones.
  - `response_cache`: Caching de respuestas frecuentes.
  - `token_usage`: Registro de uso de tokens (LLM).

### **Integración con LLM**
- **APIs**: Mistral API, OpenRouter API, Gemini API.
- **Prompt Engineering**: Diseñado para respuestas contextualizadas.

---

## 📄 **Documentación Adicional**
- [Requisitos Detallados](./docs/requirements.md)
- [Arquitectura en GCP](./docs/gcp_architecture.md)
- [Guía de Despliegue](../README.md#-despliegue-en-gcp)
- [Diagrama de Arquitectura](./plans/architecture_diagram.md)

---

## 🚀 **Cómo Empezar**

### **1. Configurar el Proyecto**
1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/jmparejaz/agent-optimization-factory.git
   cd agent-optimization-factory
   ```

2. **Configurar `config.yaml`**:
   - Copia los valores de ejemplo y reemplaza los placeholders (`YOUR_*`).
   - Configura tus API keys (Twilio, Mistral/OpenRouter/Gemini).
   - Personaliza la base de conocimiento (empresa, productos, FAQ).

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

### **2. Inicializar Firestore**
Ejecuta el script para cargar la base de conocimiento:
```bash
python init_firestore.py --init
```

### **3. Desplegar en GCP**
Ejecuta el script de despliegue:
```bash
chmod +x .agents/scripts/deploy.sh
.agents/scripts/deploy.sh
```

### **4. Configurar Twilio**
1. Ve a [Twilio Console](https://console.twilio.com/).
2. Configura el webhook con la URL generada por el script de despliegue (ej: `https://whatsapp-agent-backend.a.run.app/webhook`).

### **5. Probar el Agente**
- Envía un mensaje de WhatsApp al número de Twilio.
- Verifica que el agente responda correctamente.

---

## 📞 **Contacto y Soporte**
- **Issues**: Reportar problemas en el repositorio.
- **Mejoras**: Propuestas en `./.agents/plans/roadmap.md`.
- **Documentación**: Consulta el [README](../README.md) para más detalles.

---

## 🔄 **Actualizaciones**
- **Última actualización**: 2024-10-01
- **Versión**: 1.0.0
- **Autor**: Equipo de Desarrollo (Agente de Optimización).

---

## **📌 Notas Importantes**
1. **Todos los parámetros son configurables en `config.yaml`**: No es necesario editar el código para cambiar configuraciones.
2. **El proyecto está diseñado para costos ≤ $50/mes**: Usa caching, límites de tokens y escalado controlado.
3. **El backend está listo para producción**: Solo necesitas configurar tus API keys y desplegar.
4. **La base de conocimiento se carga desde `config.yaml`**: Personaliza empresa, productos y FAQ allí.
