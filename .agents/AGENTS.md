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
.agents/
├── AGENTS.md                    # Este documento (visión general)
├── docs/                        # Documentación técnica y guías
│   ├── requirements.md          # Requisitos detallados del proyecto
│   ├── gcp_architecture.md      # Arquitectura en GCP
│   ├── gcp_services.md          # Servicios GCP utilizados y costos
│   ├── deployment.md            # Guía de despliegue en GCP
│   ├── user_guide.md            # Guía para usuarios finales
│   └── maintenance.md           # Guía de mantenimiento y monitoreo
├── plans/                       # Planificación y estrategia
│   ├── master_plan.md           # Plan maestro (este documento extendido)
│   ├── architecture_diagram.md # Diagrama de arquitectura (Mermaid)
│   └── scaling_plan.md          # Plan de escalamiento futuro
├── workflows/                   # Flujos de trabajo del agente
│   ├── whatsapp_webhook.md      # Flujo del webhook de WhatsApp
│   ├── llm_integration.md       # Integración con Mistral/Gemini/OpenRouter
│   └── customer_service.md      # Flujo de servicio al cliente
├── skills/                      # Habilidades del agente (módulos de código)
│   ├── whatsapp_handler.py      # Manejo de mensajes de WhatsApp
│   ├── llm_client.py            # Cliente para Mistral/Gemini/OpenRouter
│   ├── knowledge_base.py        # Base de conocimiento (empresa, productos, FAQ)
│   └── response_generator.py    # Generador de respuestas contextualizadas
├── scripts/                     # Scripts de automatización
│   ├── deploy.sh                # Script para desplegar en GCP
│   ├── monitor.sh               # Script para monitorear costos
│   └── test_webhook.py          # Pruebas locales del webhook
└── communication/               # Comunicación del equipo
    └── team_updates.md          # Actualizaciones y decisiones del equipo
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
- [ ] Crear proyecto en GCP y habilitar servicios (Cloud Run, Firestore).
- [ ] Configurar cuenta en Twilio y WhatsApp Sandbox.
- [ ] Desarrollar esqueleto del backend (FastAPI/Flask + Twilio).
- [ ] Probar webhook localmente con ngrok.

**Entregables**:
- Proyecto GCP configurado.
- Cuenta Twilio funcional.
- Código base del backend en `./src/`.

---

### **🔹 Fase 2: Base de Conocimiento y LLM (Días 3-4)**
- [ ] Crear base de conocimiento en Firestore (empresa, productos, FAQ).
- [ ] Integrar Mistral/OpenRouter para generar respuestas.
- [ ] Desarrollar lógica de respuestas (combinar base de conocimiento + LLM).

**Entregables**:
- Base de conocimiento en Firestore.
- Integración funcional con Mistral/OpenRouter.
- Respuestas automáticas básicas.

---

### **🔹 Fase 3: Pruebas y Despliegue (Días 5-6)**
- [ ] Pruebas locales con ngrok (simular webhook de Twilio).
- [ ] Desplegar backend en Cloud Run.
- [ ] Configurar monitoreo básico (Cloud Logging).

**Entregables**:
- Agente funcional en producción.
- Documentación de despliegue (`./.agents/docs/deployment.md`).
- Pruebas con 5-10 mensajes reales.

---

### **🔹 Fase 4: Optimización y Documentación (Día 7)**
- [ ] Optimizar costos (ajustar Cloud Run, reducir tokens en LLM).
- [ ] Documentar guías de usuario y mantenimiento.
- [ ] Plan de escalamiento para +100 usuarios/día.

**Entregables**:
- Documentación completa.
- Agente listo para uso real.

---

## 🛠️ **Requisitos Técnicos**

### **Backend (Cloud Run)**
- **Lenguaje**: Python 3.10+ (FastAPI o Flask).
- **Dependencias**:
  ```bash
  fastapi==0.109.0
  uvicorn==0.27.0
  twilio==9.0.0
  google-cloud-firestore==2.11.1
  requests==2.31.0
  python-dotenv==1.0.0
  ```

### **Base de Conocimiento (Firestore)**
- **Colecciones**:
  - `company_info`: Descripción de la empresa.
  - `products`: Lista de productos y precios.
  - `faq`: Preguntas frecuentes y respuestas.
  - `chat_sessions`: Historial de conversaciones.

### **Integración con LLM**
- **API Keys**: Se requieren claves para Mistral/OpenRouter/Gemini.
- **Prompt Engineering**: Diseñar prompts para respuestas contextualizadas.
  Ejemplo:
  ```text
  Eres un asistente de ventas de [Nombre de la Empresa]. 
  Contexto: {company_description}.
  Productos disponibles: {products}.
  Responde la siguiente pregunta de un cliente: {user_message}.
  ```

---

## 📄 **Documentación Adicional**
- [Requisitos Detallados](./docs/requirements.md)
- [Arquitectura en GCP](./docs/gcp_architecture.md)
- [Guía de Despliegue](./docs/deployment.md)
- [Diagrama de Arquitectura](./plans/architecture_diagram.md)

---

## 🚀 **Cómo Empezar**
1. **Clonar este repositorio** y navegar a `.agents/`.
2. **Configurar GCP**:
   ```bash
   gcloud init
   gcloud services enable run.googleapis.com firestore.googleapis.com
   ```
3. **Configurar Twilio**:
   - Crear cuenta en [Twilio](https://www.twilio.com/try-twilio).
   - Habilitar WhatsApp Sandbox.
4. **Desplegar el backend**:
   ```bash
   cd .agents/scripts
   chmod +x deploy.sh
   ./deploy.sh
   ```

---

## 📞 **Contacto y Soporte**
- **Issues**: Reportar problemas en el repositorio.
- **Mejoras**: Propuestas en `./.agents/plans/roadmap.md`.

---

## 🔄 **Actualizaciones**
- **Última actualización**: 2024-10-01
- **Versión**: 1.0.0
- **Autor**: Equipo de Desarrollo (Agente de Optimización).
