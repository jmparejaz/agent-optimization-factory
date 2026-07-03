#!/bin/bash

# 🚀 Script de Despliegue para el Agente de WhatsApp en GCP
# Este script automatiza el despliegue del backend en Cloud Run usando config.yaml.
# Todos los parámetros se cargan desde config.yaml.

# --- Configuración Inicial ---
set -e  # Salir si hay un error
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# --- Colores para logs ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# --- Funciones de Log ---
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║ $1${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
}

# --- Validar dependencias ---
log_info "Validando dependencias..."

# Verificar gcloud
if ! command -v gcloud &> /dev/null; then
    log_error "gcloud no está instalado. Instálalo desde: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verificar que estamos autenticados en GCP
if ! gcloud auth list --format="value(account)" | grep -q "@"; then
    log_error "No estás autenticado en GCP. Ejecuta: gcloud auth login"
    exit 1
fi

# --- Cargar configuración desde config.yaml ---
CONFIG_FILE="$PROJECT_ROOT/../config.yaml"

if [ ! -f "$CONFIG_FILE" ]; then
    log_error "No se encontró config.yaml en $CONFIG_FILE"
    exit 1
fi

log_info "Cargando configuración desde $CONFIG_FILE..."

# Función para extraer valores de YAML usando grep (fallback si yq no está disponible)
get_yaml_value() {
    local key="$1"
    local file="$2"
    
    # Intentar con yq primero
    if command -v yq &> /dev/null; then
        echo "$(yq e ".$key" "$file" | tr -d '"')"
        return
    fi
    
    # Fallback con grep y awk
    local value=$(grep -E "^\s*${key}:" "$file" | head -1 | awk -F: '{print $2}' | tr -d '" ')
    echo "$value"
}

# Extraer valores de config.yaml
PROJECT_ID=$(get_yaml_value "gcp.project_id" "$CONFIG_FILE")
REGION=$(get_yaml_value "gcp.region" "$CONFIG_FILE")
SERVICE_NAME=$(get_yaml_value "gcp.cloud_run.service_name" "$CONFIG_FILE")
MEMORY=$(get_yaml_value "gcp.cloud_run.memory" "$CONFIG_FILE")
CPU=$(get_yaml_value "gcp.cloud_run.cpu" "$CONFIG_FILE")
MAX_INSTANCES=$(get_yaml_value "gcp.cloud_run.max_instances" "$CONFIG_FILE")
TIMEOUT=$(get_yaml_value "gcp.cloud_run.timeout" "$CONFIG_FILE")

# Validar que se cargaron los valores
if [ -z "$PROJECT_ID" ]; then
    log_error "No se pudo leer project_id de config.yaml"
    exit 1
fi

log_info "Usando proyecto de GCP: $PROJECT_ID"
log_info "Región: $REGION"
log_info "Nombre del servicio: $SERVICE_NAME"
log_info "Memoria: $MEMORY"
log_info "CPU: $CPU"
log_info "Máximo de instancias: $MAX_INSTANCES"
log_info "Timeout: $TIMEOUT segundos"

# --- Habilitar servicios de GCP ---
log_info "Habilitando servicios de GCP..."

gcloud services enable run.googleapis.com --project="$PROJECT_ID" || {
    log_error "No se pudo habilitar Cloud Run. Verifica permisos."
    exit 1
}

gcloud services enable firestore.googleapis.com --project="$PROJECT_ID" || {
    log_error "No se pudo habilitar Firestore. Verifica permisos."
    exit 1
}

gcloud services enable secretmanager.googleapis.com --project="$PROJECT_ID" || {
    log_warning "No se pudo habilitar Secret Manager. Usarás variables de entorno directamente."
}

# --- Construir la imagen del contenedor ---
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"
log_info "Construyendo imagen del contenedor: $IMAGE_NAME"

# Usar Cloud Build para construir la imagen
if [ -f "$PROJECT_ROOT/../Dockerfile" ]; then
    log_info "Construyendo con Cloud Build..."
    gcloud builds submit \
        --tag "$IMAGE_NAME" \
        --project="$PROJECT_ID" \
        "$PROJECT_ROOT/.." || {
        log_error "Fallo al construir la imagen con Cloud Build."
        exit 1
    }
else
    log_error "No se encontró Dockerfile en $PROJECT_ROOT/../"
    exit 1
fi

log_success "Imagen construida: $IMAGE_NAME"

# --- Desplegar en Cloud Run ---
log_info "Desplegando en Cloud Run..."

# Verificar si el servicio ya existe
if gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" &> /dev/null; then
    log_info "El servicio $SERVICE_NAME ya existe. Actualizando..."
    ACTION="update"
else
    log_info "Creando nuevo servicio $SERVICE_NAME..."
    ACTION="deploy"
fi

# Desplegar o actualizar el servicio
gcloud run $ACTION "$SERVICE_NAME" \
    --image "$IMAGE_NAME" \
    --platform managed \
    --region "$REGION" \
    --memory "$MEMORY" \
    --cpu "$CPU" \
    --max-instances "$MAX_INSTANCES" \
    --timeout "$TIMEOUT" \
    --allow-unauthenticated \
    --project="$PROJECT_ID" || {
    log_error "Fallo al desplegar en Cloud Run."
    exit 1
}

# Obtener la URL del servicio
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" --format="value(status.url)")
log_success "Servicio desplegado en: $SERVICE_URL"

# --- Configurar Firestore ---
log_info "Configurando Firestore..."

# Crear base de datos en modo Datastore (más económico)
FIRESTORE_MODE=$(get_yaml_value "gcp.firestore.mode" "$CONFIG_FILE")
if [ "$FIRESTORE_MODE" = "datastore" ]; then
    if ! gcloud firestore databases list --project="$PROJECT_ID" | grep -q "datastore"; then
        gcloud firestore databases create \
            --region="$REGION" \
            --type=firestore-native \
            --mode=datastore \
            --project="$PROJECT_ID" || {
            log_warning "No se pudo crear la base de datos de Firestore."
        }
    else
        log_info "Firestore ya está configurado en modo Datastore."
    fi
else
    log_info "Firestore está configurado en modo nativo."
fi

# --- Actualizar config.yaml con la URL del webhook ---
log_info "Actualizando config.yaml con la URL del webhook..."

# Usar sed para reemplazar la URL del webhook en config.yaml
if command -v sed &> /dev/null; then
    # Hacer backup de config.yaml
    cp "$CONFIG_FILE" "$CONFIG_FILE.bak"
    
    # Reemplazar la URL del webhook
    sed -i "s|webhook_url:.*|webhook_url: \"$SERVICE_URL/webhook\"|" "$CONFIG_FILE"
    log_success "URL del webhook actualizada en config.yaml: $SERVICE_URL/webhook"
else
    log_warning "sed no está disponible. Actualiza manualmente config.yaml con la URL: $SERVICE_URL/webhook"
fi

# --- Configurar Twilio (opcional) ---
TWILIO_ACCOUNT_SID=$(get_yaml_value "twilio.account_sid" "$CONFIG_FILE")
TWILIO_AUTH_TOKEN=$(get_yaml_value "twilio.auth_token" "$CONFIG_FILE")

if [ -n "$TWILIO_ACCOUNT_SID" ] && [ -n "$TWILIO_AUTH_TOKEN" ]; then
    log_info "Configurando Twilio..."
    log_info "Recuerda configurar el webhook en Twilio Console con la URL: $SERVICE_URL/webhook"
    log_info "Puedes hacerlo manualmente en: https://console.twilio.com/us1/develop/phone-numbers/manage"
else
    log_warning "No se configuró Twilio. Asegúrate de hacerlo manualmente."
fi

# --- Inicializar Firestore con datos de config.yaml ---
log_info "Inicializando Firestore con datos de config.yaml..."

# Ejecutar el script de inicialización
if [ -f "$PROJECT_ROOT/../init_firestore.py" ]; then
    log_info "Ejecutando init_firestore.py --init..."
    cd "$PROJECT_ROOT/.."
    python init_firestore.py --init || {
        log_warning "No se pudo inicializar Firestore. Hazlo manualmente con: python init_firestore.py --init"
    }
    cd "$SCRIPT_DIR"
else
    log_warning "No se encontró init_firestore.py. Inicializa Firestore manualmente."
fi

# --- Resumen del Despliegue ---
log_success ""
log_success "╔════════════════════════════════════════════════════════════╗"
log_success "║           🎉 DESPLIEGUE COMPLETADO CON ÉXITO 🎉            ║"
log_success "╚════════════════════════════════════════════════════════════╝"
log_success ""
log_success "📌 URL del servicio: $SERVICE_URL"
log_success "📌 Proyecto de GCP: $PROJECT_ID"
log_success "📌 Región: $REGION"
log_success ""
log_info "🔧 Pasos siguientes:"
log_info "1. Configura el webhook en Twilio con la URL: $SERVICE_URL/webhook"
log_info "   - Ve a: https://console.twilio.com/us1/develop/phone-numbers/manage"
log_info "   - Selecciona tu número de WhatsApp."
log_info "   - En 'A MESSAGE COMES IN', configura:"
log_info "     - Webhook URL: $SERVICE_URL/webhook"
log_info "     - HTTP Method: POST"
log_info ""
log_info "2. Prueba el agente enviando un mensaje a tu número de WhatsApp de Twilio."
log_info ""
log_info "3. Monitorea el servicio:"
log_info "   - Logs: https://console.cloud.google.com/logs"
log_info "   - Métricas: https://console.cloud.google.com/monitoring"
log_info "   - Costos: https://console.cloud.google.com/billing"
log_info ""
log_info "4. Usa el script de monitoreo para ver logs en tiempo real:"
log_info "   chmod +x .agents/scripts/monitor.sh"
log_info "   .agents/scripts/monitor.sh"
log_info ""
log_info "💡 Para actualizar el servicio, ejecuta este script nuevamente."
log_info "💡 Para ver los logs en tiempo real:"
log_info "   gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME' --limit 50"

# --- Verificar despliegue ---
log_info ""
log_info "Verificando despliegue..."
if curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/health" | grep -q "200"; then
    log_success "✅ El servicio está en línea y respondiendo."
    
    # Probar el endpoint de health
    HEALTH_RESPONSE=$(curl -s "$SERVICE_URL/health")
    log_success "Respuesta de health check: $HEALTH_RESPONSE"
else
    log_warning "⚠️  El servicio no respondió correctamente. Revisa los logs con:"
    log_warning "   .agents/scripts/monitor.sh"
fi
