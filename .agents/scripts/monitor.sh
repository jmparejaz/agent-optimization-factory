#!/bin/bash

# 📊 Script de Monitoreo para el Agente de WhatsApp
# Este script permite monitorear el estado, costos y logs del agente desplegado en GCP.

# --- Configuración Inicial ---
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Cargar variables de entorno desde .env (si existe)
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

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
if ! command -v gcloud &> /dev/null; then
    log_error "gcloud no está instalado. Instálalo desde: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# --- Configuración del Proyecto ---
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-}"
if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID=$(gcloud config get-value project)
fi

if [ -z "$PROJECT_ID" ]; then
    log_error "No se pudo determinar el PROJECT_ID. Configura gcloud o exporta GOOGLE_CLOUD_PROJECT."
    exit 1
fi

SERVICE_NAME="whatsapp-agent-backend"
REGION="us-central1"

# --- Menú Principal ---
show_menu() {
    clear
    log_header "MENÚ DE MONITOREO - AGENTE DE WHATSAPP"
    echo ""
    echo "Selecciona una opción:"
    echo ""
    echo "  ${CYAN}1${NC}. Ver estado del servicio en Cloud Run"
    echo "  ${CYAN}2${NC}. Ver logs en tiempo real"
    echo "  ${CYAN}3${NC}. Ver logs históricos (últimas 100 líneas)"
    echo "  ${CYAN}4${NC}. Ver métricas de Cloud Run"
    echo "  ${CYAN}5${NC}. Ver uso de Firestore"
    echo "  ${CYAN}6${NC}. Ver costo estimado actual"
    echo "  ${CYAN}7${NC}. Ver alertas de GCP"
    echo "  ${CYAN}8${NC}. Probar el webhook manualmente"
    echo "  ${CYAN}9${NC}. Ver información del proyecto"
    echo "  ${CYAN}0${NC}. Salir"
    echo ""
    echo -n "Opción: "
}

# --- Funciones de Monitoreo ---

# 1. Ver estado del servicio en Cloud Run
check_service_status() {
    log_header "ESTADO DEL SERVICIO EN CLOUD RUN"
    
    echo ""
    log_info "Obteniendo información del servicio $SERVICE_NAME..."
    
    # Verificar si el servicio existe
    if ! gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" &> /dev/null; then
        log_error "El servicio $SERVICE_NAME no existe en $REGION."
        return
    fi
    
    # Obtener detalles del servicio
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" --format="value(status.url)")
    SERVICE_STATUS=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" --format="value(status.conditions[0].status)")
    SERVICE_REVISION=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" --format="value(status.latestCreatedRevisionName)")
    SERVICE_CPU=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" --format="value(spec.template.spec.containers[0].resources.limits.cpu)")
    SERVICE_MEMORY=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" --format="value(spec.template.spec.containers[0].resources.limits.memory)")
    
    echo ""
    log_success "Nombre del servicio: $SERVICE_NAME"
    log_success "URL: $SERVICE_URL"
    log_success "Estado: $SERVICE_STATUS"
    log_success "Revisión: $SERVICE_REVISION"
    log_success "CPU: $SERVICE_CPU"
    log_success "Memoria: $SERVICE_MEMORY"
    echo ""
    
    # Verificar si el servicio está en línea
    if curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/health" | grep -q "200"; then
        log_success "✅ El servicio está en línea y respondiendo."
    else
        log_error "❌ El servicio no respondió correctamente."
    fi
    
    echo ""
    echo "Presiona Enter para continuar..."
    read -r
}

# 2. Ver logs en tiempo real
view_realtime_logs() {
    log_header "LOGS EN TIEMPO REAL"
    
    echo ""
    log_info "Mostrando logs en tiempo real (Ctrl+C para detener)..."
    echo ""
    
    gcloud logging read \
        "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
        --project="$PROJECT_ID" \
        --format="json" \
        --stream
}

# 3. Ver logs históricos
view_historical_logs() {
    log_header "LOGS HISTÓRICOS (ÚLTIMAS 100 LÍNEAS)"
    
    echo ""
    log_info "Mostrando últimos 100 logs..."
    echo ""
    
    gcloud logging read \
        "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
        --project="$PROJECT_ID" \
        --limit=100 \
        --format="table(timestamp,severity,jsonPayload.message)"
    
    echo ""
    echo "Presiona Enter para continuar..."
    read -r
}

# 4. Ver métricas de Cloud Run
view_metrics() {
    log_header "MÉTRICAS DE CLOUD RUN"
    
    echo ""
    log_info "Obteniendo métricas de los últimos 5 minutos..."
    echo ""
    
    # Métricas de solicitudes
    echo "📊 Solicitudes:"
    gcloud monitoring metrics read \
        "run.googleapis.com/request_count" \
        --project="$PROJECT_ID" \
        --filter="resource.service_name=$SERVICE_NAME" \
        --format="table(value.int64Value)" \
        --interval=5m
    
    echo ""
    
    # Métricas de latencia
    echo "⏱️  Latencia (promedio):"
    gcloud monitoring metrics read \
        "run.googleapis.com/request_latencies" \
        --project="$PROJECT_ID" \
        --filter="resource.service_name=$SERVICE_NAME" \
        --format="table(value.doubleValue)" \
        --interval=5m
    
    echo ""
    
    # Métricas de instancias
    echo "🖥️  Instancias activas:"
    gcloud monitoring metrics read \
        "run.googleapis.com/container/instance_count" \
        --project="$PROJECT_ID" \
        --filter="resource.service_name=$SERVICE_NAME" \
        --format="table(value.int64Value)" \
        --interval=5m
    
    echo ""
    echo "Presiona Enter para continuar..."
    read -r
}

# 5. Ver uso de Firestore
view_firestore_usage() {
    log_header "USO DE FIRESTORE"
    
    echo ""
    log_info "Obteniendo métricas de Firestore..."
    echo ""
    
    # Operaciones de lectura
    echo "📖 Lecturas:"
    gcloud monitoring metrics read \
        "firestore.googleapis.com/document/read_count" \
        --project="$PROJECT_ID" \
        --format="table(value.int64Value)" \
        --interval=1h
    
    echo ""
    
    # Operaciones de escritura
    echo "✏️  Escrituras:"
    gcloud monitoring metrics read \
        "firestore.googleapis.com/document/write_count" \
        --project="$PROJECT_ID" \
        --format="table(value.int64Value)" \
        --interval=1h
    
    echo ""
    
    # Almacenamiento
    echo "💾 Almacenamiento (GB):"
    gcloud monitoring metrics read \
        "firestore.googleapis.com/database/storage" \
        --project="$PROJECT_ID" \
        --format="table(value.doubleValue)" \
        --interval=1h
    
    echo ""
    echo "Presiona Enter para continuar..."
    read -r
}

# 6. Ver costo estimado actual
view_cost() {
    log_header "COSTO ESTIMADO ACTUAL"
    
    echo ""
    log_info "Obteniendo costo estimado para hoy..."
    echo ""
    
    # Obtener costo de Cloud Run
    echo "💰 Costo de Cloud Run (hoy):"
    gcloud beta billing accounts list --project="$PROJECT_ID" --format="value(name)" | xargs -I {} gcloud beta billing accounts describe {} --format="value(cost)"
    
    echo ""
    
    # Obtener costo detallado por servicio
    echo "📋 Desglose por servicio (últimos 30 días):"
    gcloud beta billing accounts list --project="$PROJECT_ID" --format="value(name)" | xargs -I {} gcloud beta billing accounts report {} \
        --start-date=$(date -d "30 days ago" +%Y-%m-%d) \
        --end-date=$(date +%Y-%m-%d) \
        --format="table(service.description, cost)"
    
    echo ""
    log_warning "Nota: Los costos pueden tardar hasta 24 horas en actualizarse."
    echo ""
    echo "Presiona Enter para continuar..."
    read -r
}

# 7. Ver alertas de GCP
view_alerts() {
    log_header "ALERTAS DE GCP"
    
    echo ""
    log_info "Obteniendo alertas activas..."
    echo ""
    
    gcloud alpha monitoring policies list --project="$PROJECT_ID" --format="table(displayName, conditions.displayName, state)"
    
    echo ""
    echo "Presiona Enter para continuar..."
    read -r
}

# 8. Probar el webhook manualmente
 test_webhook() {
    log_header "PRUEBA MANUAL DEL WEBHOOK"
    
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --project="$PROJECT_ID" --format="value(status.url)")
    
    echo ""
    log_info "URL del webhook: $SERVICE_URL/webhook"
    echo ""
    
    # Solicitar mensaje al usuario
    echo -n "Ingresa el mensaje de prueba (o presiona Enter para usar un mensaje por defecto): "
    read -r MESSAGE
    
    if [ -z "$MESSAGE" ]; then
        MESSAGE="Hola, ¿qué productos tienen?"
    fi
    
    echo ""
    log_info "Enviando mensaje de prueba: '$MESSAGE'"
    echo ""
    
    # Enviar solicitud POST al webhook
    RESPONSE=$(curl -s -X POST \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "Body=$MESSAGE" \
        -d "From=whatsapp:+1234567890" \
        -d "To=whatsapp:+14155238886" \
        "$SERVICE_URL/webhook")
    
    echo "📩 Respuesta del webhook:"
    echo "$RESPONSE"
    echo ""
    
    echo "Presiona Enter para continuar..."
    read -r
}

# 9. Ver información del proyecto
view_project_info() {
    log_header "INFORMACIÓN DEL PROYECTO"
    
    echo ""
    log_success "Nombre del proyecto: $PROJECT_ID"
    log_success "Región: $REGION"
    log_success "Servicio: $SERVICE_NAME"
    echo ""
    
    # Listar servicios de GCP habilitados
    echo "🔧 Servicios de GCP habilitados:"
    gcloud services list --enabled --project="$PROJECT_ID" --format="table(config.name)"
    
    echo ""
    
    # Listar recursos de Cloud Run
    echo "☁️  Servicios de Cloud Run:"
    gcloud run services list --project="$PROJECT_ID" --format="table(name,region,url)"
    
    echo ""
    
    # Listar colecciones de Firestore
    echo "🗃️  Colecciones de Firestore:"
    gcloud firestore collections list --project="$PROJECT_ID" --format="table(collectionId)"
    
    echo ""
    echo "Presiona Enter para continuar..."
    read -r
}

# --- Bucle Principal ---
while true; do
    show_menu
    read -r OPTION
    
    case $OPTION in
        1)
            check_service_status
            ;;
        2)
            view_realtime_logs
            ;;
        3)
            view_historical_logs
            ;;
        4)
            view_metrics
            ;;
        5)
            view_firestore_usage
            ;;
        6)
            view_cost
            ;;
        7)
            view_alerts
            ;;
        8)
            test_webhook
            ;;
        9)
            view_project_info
            ;;
        0)
            log_info "Saliendo..."
            exit 0
            ;;
        *)
            log_error "Opción no válida. Intenta de nuevo."
            ;;
    esac
done
