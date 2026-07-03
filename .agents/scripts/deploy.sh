#!/bin/bash

# 🚀 Script de Despliegue para el Agente de WhatsApp en GCP
# Este script automatiza el despliegue del backend en Cloud Run.

# --- Configuración Inicial ---
set -e  # Salir si hay un error
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Cargar variables de entorno desde .env (si existe)
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "🔍 Cargando variables de entorno desde .env..."
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

# --- Colores para logs ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# --- Validar dependencias ---
log_info "Validando dependencias..."

# Verificar gcloud
if ! command -v gcloud &> /dev/null; then
    log_error "gcloud no está instalado. Instálalo desde: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Verificar Docker (opcional, solo si se usa Docker localmente)
if ! command -v docker &> /dev/null; then
    log_warning "Docker no está instalado. Se usará Cloud Build para construir la imagen."
fi

# Verificar que estamos autenticados en GCP
if ! gcloud auth list --format="value(account)" | grep -q "@"; then
    log_error "No estás autenticado en GCP. Ejecuta: gcloud auth login"
    exit 1
fi

# --- Configuración del Proyecto ---
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-}"
if [ -z "$PROJECT_ID" ]; then
    log_info "No se especificó GOOGLE_CLOUD_PROJECT. Usando el proyecto actual de gcloud..."
    PROJECT_ID=$(gcloud config get-value project)
fi

if [ -z "$PROJECT_ID" ]; then
    log_error "No se pudo determinar el PROJECT_ID. Configura gcloud o exporta GOOGLE_CLOUD_PROJECT."
    exit 1
fi

log_info "Usando proyecto de GCP: $PROJECT_ID"

# --- Configuración del Backend ---
SERVICE_NAME="whatsapp-agent-backend"
REGION="us-central1"
MEMORY="2Gi"
CPU="1"
MAX_INSTANCES="1"
TIMEOUT="300"  # 5 minutos

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
if [ -f "$PROJECT_ROOT/Dockerfile" ]; then
    log_info "Construyendo con Cloud Build..."
    gcloud builds submit \
        --tag "$IMAGE_NAME" \
        --project="$PROJECT_ID" \
        "$PROJECT_ROOT" || {
        log_error "Fallo al construir la imagen con Cloud Build."
        exit 1
    }
else
    log_error "No se encontró Dockerfile en $PROJECT_ROOT"
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

# --- Configurar variables de entorno ---
log_info "Configurando variables de entorno..."

# Variables obligatorias (validar que existan)
if [ -z "$TWILIO_ACCOUNT_SID" ] || [ -z "$TWILIO_AUTH_TOKEN" ]; then
    log_error "Faltan variables de entorno obligatorias: TWILIO_ACCOUNT_SID o TWILIO_AUTH_TOKEN"
    exit 1
fi

if [ -z "$MISTRAL_API_KEY" ] && [ -z "$OPENROUTER_API_KEY" ] && [ -z "$GEMINI_API_KEY" ]; then
    log_error "Falta al menos una API key de LLM: MISTRAL_API_KEY, OPENROUTER_API_KEY o GEMINI_API_KEY"
    exit 1
fi

# Actualizar el servicio con variables de entorno
gcloud run services update "$SERVICE_NAME" \
    --region "$REGION" \
    --project="$PROJECT_ID" \
    --set-env-vars "TWILIO_ACCOUNT_SID=$TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN=$TWILIO_AUTH_TOKEN" \
    --set-env-vars "MISTRAL_API_KEY=$MISTRAL_API_KEY,OPENROUTER_API_KEY=$OPENROUTER_API_KEY,GEMINI_API_KEY=$GEMINI_API_KEY" \
    --set-env-vars "LLM_MODEL=${LLM_MODEL:-mistral-tiny}" \
    --set-env-vars "GOOGLE_APPLICATION_CREDENTIALS=/var/secrets/google/key.json" || {
    log_warning "No se pudieron configurar todas las variables de entorno."
}

# --- Configurar Secret Manager (opcional) ---
if command -v gcloud &> /dev/null && gcloud services list --enabled --project="$PROJECT_ID" | grep -q secretmanager; then
    log_info "Configurando Secret Manager..."
    
    # Crear secretos si no existen
    if ! gcloud secrets list --project="$PROJECT_ID" | grep -q "twilio_account_sid"; then
        echo -n "$TWILIO_ACCOUNT_SID" | gcloud secrets create twilio_account_sid --data-file=- --project="$PROJECT_ID"
    fi
    
    if ! gcloud secrets list --project="$PROJECT_ID" | grep -q "twilio_auth_token"; then
        echo -n "$TWILIO_AUTH_TOKEN" | gcloud secrets create twilio_auth_token --data-file=- --project="$PROJECT_ID"
    fi
    
    if [ -n "$MISTRAL_API_KEY" ] && ! gcloud secrets list --project="$PROJECT_ID" | grep -q "mistral_api_key"; then
        echo -n "$MISTRAL_API_KEY" | gcloud secrets create mistral_api_key --data-file=- --project="$PROJECT_ID"
    fi
    
    log_success "Secretos configurados en Secret Manager."
else
    log_warning "Secret Manager no está habilitado. Usando variables de entorno directamente."
fi

# --- Configurar Firestore ---
log_info "Configurando Firestore..."

# Crear base de datos en modo Datastore (más económico)
if ! gcloud firestore databases list --project="$PROJECT_ID" | grep -q "datastore"; then
    gcloud firestore databases create \
        --region="$REGION" \
        --type=firestore-native \
        --mode=datastore \
        --project="$PROJECT_ID" || {
        log_warning "No se pudo crear la base de datos de Firestore."
    }
else
    log_info "Firestore ya está configurado."
fi

# --- Configurar Twilio (opcional) ---
if [ -n "$TWILIO_ACCOUNT_SID" ] && [ -n "$TWILIO_AUTH_TOKEN" ]; then
    log_info "Configurando Twilio..."
    log_info "Recuerda configurar el webhook en Twilio Console con la URL: $SERVICE_URL/webhook"
    log_info "Puedes hacerlo manualmente en: https://console.twilio.com/us1/develop/phone-numbers/manage"
else
    log_warning "No se configuró Twilio. Asegúrate de hacerlo manualmente."
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
log_info "2. Prueba el agente enviando un mensaje a tu número de WhatsApp de Twilio."
log_info "3. Monitorea los logs en: https://console.cloud.google.com/logs"
log_info "4. Revisa el costo en: https://console.cloud.google.com/billing"
log_info ""
log_info "💡 Para actualizar el servicio, ejecuta este script nuevamente."
log_info "💡 Para ver los logs en tiempo real: gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME' --limit 50"

# --- Verificar despliegue ---
log_info ""
log_info "Verificando despliegue..."
if curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/health" | grep -q "200"; then
    log_success "✅ El servicio está en línea y respondiendo."
else
    log_warning "⚠️  El servicio no respondió correctamente. Revisa los logs."
fi
