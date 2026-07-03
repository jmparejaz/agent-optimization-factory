# 📋 Requisitos del Agente de WhatsApp para Servicio al Cliente y Ventas

## 🎯 **Objetivo General**
Desarrollar un **agente de WhatsApp** que automatice la atención al cliente y ventas, respondiendo preguntas basadas en la descripción de la empresa, productos y preguntas frecuentes (FAQ), utilizando modelos de lenguaje (LLM) como **Mistral API**, **Gemini API** o **OpenRouter API**. El sistema debe estar desplegado en **Google Cloud Platform (GCP)** con un **costo máximo de $50/mes** y soportar **~100 usuarios/día**.

---

## 📌 **Requisitos Funcionales**

### **1. Integración con WhatsApp**
- **RF-001**: El agente debe recibir mensajes de clientes nuevos y existentes a través de **WhatsApp**.
- **RF-002**: Debe responder automáticamente a los mensajes entrantes.
- **RF-003**: Debe soportar **mensajes de texto** (no se requiere soporte para multimedia en esta fase).
- **RF-004**: Debe manejar **sesiones de chat** (contexto de conversación previa).
- **RF-005**: Debe notificar al equipo humano si no puede responder una pregunta (opcional en fase inicial).

### **2. Base de Conocimiento**
- **RF-010**: El agente debe tener acceso a la **descripción de la empresa** (misión, visión, valores).
- **RF-011**: Debe conocer la **lista de productos/servicios** ofrecidos, incluyendo:
  - Nombre del producto.
  - Descripción.
  - Precio.
  - Características principales.
- **RF-012**: Debe responder **preguntas frecuentes (FAQ)** predefinidas.
- **RF-013**: La base de conocimiento debe ser **fácilmente actualizable** (sin requerir redepliegue).

### **3. Generación de Respuestas**
- **RF-020**: Las respuestas deben generarse utilizando un **modelo de lenguaje (LLM)**.
- **RF-021**: El LLM debe ser **Mistral API**, **Gemini API** o **OpenRouter API** (priorizar Mistral por costo).
- **RF-022**: Las respuestas deben ser **contextualizadas** con la base de conocimiento.
- **RF-023**: Debe manejar **preguntas abiertas** (no solo FAQ).
- **RF-024**: Debe **evitar respuestas genéricas** (ej: "No sé", "Consulte con un agente").

### **4. Escalabilidad y Rendimiento**
- **RF-030**: Debe soportar **100 usuarios/día** (con picos de hasta 20 mensajes simultáneos).
- **RF-031**: El tiempo de respuesta debe ser **< 5 segundos** en el 90% de los casos.
- **RF-032**: Debe ser **escalable** a 500 usuarios/día con cambios mínimos.

### **5. Monitoreo y Mantenimiento**
- **RF-040**: Debe registrar **logs de todas las interacciones** (mensajes entrantes/salientes).
- **RF-041**: Debe monitorear el **uso de tokens en el LLM** para controlar costos.
- **RF-042**: Debe alertar si el **costo mensual supera $40** (para evitar sorpresas).

---

## 📌 **Requisitos No Funcionales**

### **1. Infraestructura**
- **RNF-001**: Desplegado en **Google Cloud Platform (GCP)**.
- **RNF-002**: Usar servicios **serverless** (Cloud Run, Cloud Functions) para reducir costos.
- **RNF-003**: **Base de datos**: Firestore (modo Datastore para reducir costos).
- **RNF-004**: **Almacenamiento**: Cloud Storage (opcional, para logs o archivos temporales).

### **2. Costos**
- **RNF-010**: **Costo máximo mensual**: $50.
- **RNF-011**: Priorizar servicios **gratis o de bajo costo** en GCP.
- **RNF-012**: Usar **Mistral API** como LLM principal (más económico).

### **3. Seguridad**
- **RNF-020**: **API Keys** (Twilio, LLM) deben almacenarse en **Secret Manager** o variables de entorno.
- **RNF-021**: Validar **origen de mensajes** (evitar spam o mensajes no autorizados).
- **RNF-022**: **Cifrar datos sensibles** (ej: información de clientes).

### **4. Disponibilidad**
- **RNF-030**: **Disponibilidad del 99%** (aceptable para fase inicial).
- **RNF-031**: **Tiempo de actividad (uptime)**: Monitorear con Cloud Monitoring.

---

## 📌 **Restricciones**
- **C-001**: Presupuesto máximo de **$50/mes** (incluye GCP + Twilio + LLM).
- **C-002**: No usar **servidores dedicados** (solo serverless).
- **C-003**: No soportar **llamadas de voz o video** (solo texto).
- **C-004**: No integrar **pagos** en esta fase (solo información de productos).

---

## 📌 **Supuestos**
- **A-001**: El agente **no reemplaza** completamente a un humano (solo automatiza respuestas comunes).
- **A-002**: Los clientes **no envían imágenes o videos** (solo texto).
- **A-003**: La base de conocimiento **no cambia frecuentemente** (actualizaciones semanales).
- **A-004**: El **idioma principal** es español (puede añadirse inglés luego).

---

## 📌 **Criterios de Aceptación**

### **Para el MVP (Fase 1)**
- [ ] El agente **recibe mensajes de WhatsApp** y responde automáticamente.
- [ ] Las respuestas son **coherentes** con la base de conocimiento.
- [ ] El **costo mensual** no supera $50 en pruebas con 100 usuarios/día.
- [ ] El **tiempo de respuesta** es < 5 segundos.

### **Para la Versión Final**
- [ ] El agente **mantiene contexto** en una conversación (ej: recuerda productos mencionados antes).
- [ ] **Notifica a un humano** cuando no puede responder (opcional).
- [ ] **Logs completos** de todas las interacciones.

---

## 📌 **Priorización de Requisitos**
| **ID**   | **Requisito**                          | **Prioridad** | **Fase** | **Estado**      |
|----------|----------------------------------------|---------------|----------|-----------------|
| RF-001   | Recibir mensajes de WhatsApp           | Alta          | 1        | Pendiente       |
| RF-002   | Responder automáticamente              | Alta          | 1        | Pendiente       |
| RF-010   | Base de conocimiento (empresa)         | Alta          | 1        | Pendiente       |
| RF-011   | Base de conocimiento (productos)       | Alta          | 1        | Pendiente       |
| RF-020   | Generar respuestas con LLM             | Alta          | 1        | Pendiente       |
| RF-021   | Usar Mistral/Gemini/OpenRouter         | Alta          | 1        | Pendiente       |
| RF-030   | Soportar 100 usuarios/día              | Alta          | 1        | Pendiente       |
| RNF-001  | Desplegado en GCP                      | Alta          | 1        | Pendiente       |
| RNF-010  | Costo máximo $50/mes                   | Alta          | 1        | Pendiente       |
| RF-005   | Notificar a humano si no responde       | Media         | 2        | Pendiente       |
| RF-032   | Escalable a 500 usuarios/día            | Media         | 2        | Pendiente       |
| RNF-020  | API Keys en Secret Manager              | Media         | 2        | Pendiente       |

---

## 📌 **Glosario**
| **Término**         | **Definición**                                                                 |
|---------------------|-------------------------------------------------------------------------------|
| LLM                 | Modelo de Lenguaje Grande (ej: Mistral, Gemini).                            |
| Webhook             | Endpoint HTTP que recibe notificaciones (ej: mensajes de Twilio).          |
| Serverless          | Servicios que se ejecutan bajo demanda (ej: Cloud Run, Cloud Functions).    |
| Token               | Unidad de texto para LLM (1 token ≈ 0.75 palabras).                         |
| Firestore           | Base de datos NoSQL de Google Cloud.                                          |

---

## 📌 **Referencias**
- [Twilio WhatsApp API](https://www.twilio.com/whatsapp)
- [Mistral API](https://mistral.ai/)
- [Gemini API](https://ai.google.dev/)
- [OpenRouter API](https://openrouter.ai/)
- [Google Cloud Run](https://cloud.google.com/run)
- [Google Firestore](https://cloud.google.com/firestore)

---

## 📅 **Historial de Cambios**
| **Versión** | **Fecha**       | **Autor**               | **Cambios**                                  |
|-------------|-----------------|-------------------------|---------------------------------------------|
| 1.0         | 2024-10-01      | Equipo de Desarrollo    | Versión inicial.                            |
