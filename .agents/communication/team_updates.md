# 📢 Actualizaciones del Equipo - Agente de WhatsApp

## 📌 **Objetivo**
Este documento registra las **actualizaciones, decisiones y avances** del equipo durante el desarrollo del agente de WhatsApp para servicio al cliente y ventas.

---

## 📅 **Cronología de Actualizaciones**

### **🔹 2024-10-01 - Inicio del Proyecto**
- **Responsable**: PM (Usuario) + Arquitecto (Agente)
- **Acciones**:
  - Definición de **requisitos** del proyecto (ver [`requirements.md`](../docs/requirements.md)).
  - Diseño de la **arquitectura en GCP** (ver [`gcp_architecture.md`](../docs/gcp_architecture.md)).
  - Creación del **plan maestro** (ver [`master_plan.md`](../plans/master_plan.md)).
  - Estructura de directorios `.agents/` configurada.

- **Decisiones**:
  - **Proveedor de WhatsApp**: Twilio (por facilidad y bajo costo).
  - **LLM principal**: Mistral API (`mistral-tiny`) por su bajo costo.
  - **Infraestructura**: Cloud Run + Firestore (modo Datastore) para mantener costos ≤ $50/mes.
  - **Escalabilidad**: Diseño para soportar **100 usuarios/día** (con margen para crecer).

- **Documentación generada**:
  - [`AGENTS.md`](../AGENTS.md)
  - [`requirements.md`](../docs/requirements.md)
  - [`gcp_architecture.md`](../docs/gcp_architecture.md)
  - [`master_plan.md`](../plans/master_plan.md)
  - [`architecture_diagram.md`](../plans/architecture_diagram.md)

---

### **🔹 2024-10-01 - Desarrollo de Workflows**
- **Responsable**: Arquitecto (Agente)
- **Acciones**:
  - Diseño del **flujo del webhook de WhatsApp** (ver [`whatsapp_webhook.md`](../workflows/whatsapp_webhook.md)).
  - Diseño de la **integración con LLM** (ver [`llm_integration.md`](../workflows/llm_integration.md)).
  - Diseño del **flujo de servicio al cliente** (ver [`customer_service.md`](../workflows/customer_service.md)).

- **Decisiones**:
  - **Detección de intenciones**: Usar **palabras clave** para preguntas comunes y **LLM** para mensajes ambiguos.
  - **Caching**: Implementar caching de respuestas frecuentes en Firestore para reducir costos.
  - **Escalamiento a humanos**: Notificar vía **email** o **Slack** cuando el agente no pueda responder.

---

### **🔹 2024-10-01 - Desarrollo de Skills (Habilidades)**
- **Responsable**: Desarrollador Backend + Desarrollador de IA (Agentes)
- **Acciones**:
  - Implementación de **`whatsapp_handler.py`** (manejo de mensajes de WhatsApp).
  - Implementación de **`llm_client.py`** (integración con Mistral/OpenRouter/Gemini).
  - Implementación de **`knowledge_base.py`** (acceso a Firestore para empresa, productos, FAQ).
  - Implementación de **`response_generator.py`** (generación de respuestas contextualizadas).
  - Implementación de **`session_manager.py`** (manejo de sesiones de chat).

- **Estructura de `skills/`**:
  ```bash
  skills/
  ├── __init__.py
  ├── whatsapp_handler.py    # Manejo de WhatsApp (Twilio)
  ├── llm_client.py          # Cliente de LLM
  ├── knowledge_base.py      # Base de conocimiento
  ├── response_generator.py  # Generador de respuestas
  ├── session_manager.py     # Manejo de sesiones
  └── utils/
      ├── __init__.py
      ├── config.py           # Configuración
      └── logging.py          # Logging
  ```

---

### **🔹 2024-10-01 - Desarrollo de Scripts**
- **Responsable**: Arquitecto (Agente)
- **Acciones**:
  - Creación de **`deploy.sh`** (despliegue en Cloud Run).
  - Creación de **`monitor.sh`** (monitoreo de costos, logs, métricas).

- **Funcionalidades de `deploy.sh`**:
  - Validación de dependencias (gcloud, Docker).
  - Habilitación de servicios de GCP (Cloud Run, Firestore).
  - Construcción de imagen con Cloud Build.
  - Despliegue en Cloud Run con configuración optimizada (1 vCPU, 2GB RAM, max-instances=1).
  - Configuración de variables de entorno.

- **Funcionalidades de `monitor.sh`**:
  - Menú interactivo para monitorear:
    - Estado del servicio en Cloud Run.
    - Logs en tiempo real.
    - Métricas de Cloud Run (latencia, solicitudes, instancias).
    - Uso de Firestore (lecturas, escrituras, almacenamiento).
    - Costo estimado actual.
    - Alertas de GCP.
    - Pruebas manuales del webhook.

---

## 📌 **Tareas Pendientes**

| **Tarea**                          | **Responsable**       | **Prioridad** | **Estado**      | **Fecha Límite** |
|-----------------------------------|-----------------------|---------------|-----------------|------------------|
| Configurar proyecto en GCP         | Arquitecto Cloud     | Alta          | Pendiente       | 2024-10-02       |
| Configurar Twilio WhatsApp         | Desarrollador Backend | Alta          | Pendiente       | 2024-10-02       |
| Cargar base de conocimiento en Firestore | Desarrollador Backend | Alta | Pendiente | 2024-10-02 |
| Probar webhook localmente con ngrok | QA                   | Media         | Pendiente       | 2024-10-03       |
| Desplegar en Cloud Run             | Arquitecto Cloud     | Alta          | Pendiente       | 2024-10-03       |
| Validar respuestas con usuarios reales | QA              | Alta          | Pendiente       | 2024-10-04       |
| Optimizar costos (caching, tokens) | Desarrollador de IA  | Media         | Pendiente       | 2024-10-05       |
| Documentar guía de usuario         | PM                   | Media         | Pendiente       | 2024-10-06       |

---

## 📌 **Decisiones Clave**

### **1. Arquitectura**
- **Backend**: Cloud Run (serverless, bajo costo).
- **Base de datos**: Firestore en modo Datastore (económico).
- **LLM**: Mistral API (`mistral-tiny`) como principal.
- **WhatsApp**: Twilio (fácil de integrar, bajo costo).

### **2. Optimización de Costos**
- **Límites**:
  - Máximo **200 tokens** por respuesta.
  - **Caching** de respuestas frecuentes.
  - **1 instancia máxima** en Cloud Run.
- **Monitoreo**: Alertas si el costo supera **$40/mes**.

### **3. Flujo de Trabajo**
- **Detección de intenciones**: Palabras clave + LLM para casos ambiguos.
- **Contexto**: Mantener **últimos 10 mensajes** de la conversación.
- **Escalamiento**: Notificar a humanos si el agente no puede responder.

---

## 📌 **Problemas y Soluciones**

| **Problema**                          | **Solución**                                                                 | **Responsable**       | **Estado**      |
|--------------------------------------|-----------------------------------------------------------------------------|-----------------------|-----------------|
| Costo de LLM podría exceder $50/mes   | Implementar caching y limitar tokens.                                       | Desarrollador de IA  | Resuelto        |
| Twilio requiere aprobación para WhatsApp | Usar Twilio Sandbox para pruebas.                                         | Desarrollador Backend | Resuelto        |
| Firestore podría ser costoso          | Usar modo Datastore y limitar operaciones.                                  | Arquitecto Cloud     | Resuelto        |
| Respuestas genéricas del LLM          | Mejorar prompts y usar base de conocimiento.                                | Desarrollador de IA  | Pendiente       |

---

## 📌 **Métricas de Éxito**

### **Objetivos**
- **Costo mensual**: ≤ $50.
- **Tiempo de respuesta**: < 5 segundos (90% de los casos).
- **Precisión de respuestas**: > 80% (validación humana).
- **Disponibilidad**: 99%.

### **Monitoreo**
- **Cloud Logging**: Logs de todas las interacciones.
- **Cloud Monitoring**: Métricas de latencia, solicitudes, errores.
- **GCP Billing**: Costo en tiempo real.

---

## 📌 **Comunicación del Equipo**

### **Canales**
- **GitHub Issues**: Para reportar bugs o tareas.
- **GitHub Discussions**: Para preguntas técnicas.
- **Reuniones diarias**: 15 minutos (stand-up).
- **Reuniones semanales**: 30 minutos (review de fase).

### **Responsables**
| **Rol**               | **Nombre**               | **Contacto**               |
|-----------------------|--------------------------|----------------------------|
| Product Manager (PM)  | Usuario                 | GitHub Issues              |
| Arquitecto Cloud      | Agente (Yo)              | GitHub Discussions         |
| Desarrollador Backend | Agente (Subagente 1)     | GitHub PRs                 |
| Desarrollador de IA   | Agente (Subagente 2)     | GitHub PRs                 |
| QA                    | Agente (Subagente 3)     | GitHub Issues              |

---

## 📌 **Próximos Pasos**

### **Corto Plazo (1-2 días)**
1. **Configurar GCP y Twilio**:
   - Crear proyecto en GCP.
   - Habilitar servicios (Cloud Run, Firestore).
   - Configurar Twilio WhatsApp Sandbox.
2. **Cargar base de conocimiento**:
   - Añadir información de la empresa, productos y FAQ a Firestore.
3. **Probar localmente**:
   - Usar ngrok para simular el webhook.
   - Validar respuestas con mensajes de prueba.

### **Mediano Plazo (3-5 días)**
1. **Desplegar en producción**:
   - Ejecutar `deploy.sh` para desplegar en Cloud Run.
   - Configurar webhook de Twilio en producción.
2. **Validar con usuarios reales**:
   - Probar con 5-10 clientes reales.
   - Ajustar respuestas según feedback.

### **Largo Plazo (1 semana)**
1. **Optimizar**:
   - Implementar caching.
   - Limitar tokens.
   - Monitorear costos.
2. **Documentar**:
   - Guía de usuario.
   - Guía de despliegue.
   - Plan de escalamiento.

---

## 📅 **Historial de Cambios**

| **Versión** | **Fecha**       | **Autor**               | **Cambios**                                  |
|-------------|-----------------|-------------------------|---------------------------------------------|
| 1.0         | 2024-10-01      | Equipo de Desarrollo    | Versión inicial con estructura completa.    |

---

## 🚀 **¿Cómo Contribuir?**
1. **Revisa las tareas pendientes** y elige una.
2. **Asigna la tarea** a tu nombre en la tabla de arriba.
3. **Trabaja en tu rama**: `git checkout -b feature/nombre-de-la-tarea`.
4. **Haz commit de tus cambios**: `git commit -m "Descripción de los cambios"`.
5. **Abre un Pull Request** en GitHub.
6. **Revisa y comenta** los PRs de otros miembros.

---

## 📞 **Soporte**
- **Preguntas técnicas**: Abre un **GitHub Discussion**.
- **Bugs o tareas**: Abre un **GitHub Issue**.
- **Urgente**: Contacta al **PM** (Usuario) directamente.
