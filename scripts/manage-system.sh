#!/bin/bash

# Script de administración para SAAM
set -e

SAAM_HOME=$(dirname "$(dirname "$0")")
CONFIG_FILE="${SAAM_HOME}/config/production.yaml"

function start_system() {
    echo "Iniciando sistema SAAM..."
    docker-compose -f "${SAAM_HOME}/docker-compose.production.yml" up -d
    echo "Sistema iniciado. Verificando estado..."
    sleep 10
    check_system_status
}

function stop_system() {
    echo "Deteniendo sistema SAAM..."
    docker-compose -f "${SAAM_HOME}/docker-compose.production.yml" down
    echo "Sistema detenido"
}

function restart_system() {
    stop_system
    start_system
}

function check_system_status() {
    echo "Verificando estado de los servicios..."
    
    # Verificar servicios de infraestructura
    check_service "rabbitmq" "5672"
    check_service "postgres" "5432" 
    check_service "redis" "6379"
    
    # Verificar módulos SAAM
    check_service "saam-mcp" "8000"
    check_service "saam-met" "8001"
    check_service "saam-sm3" "health"
    check_service "saam-mao" "health"
    
    echo "Todos los servicios están operativos"
}

function check_service() {
    local service=$1
    local port=$2
    
    if docker-compose -f "${SAAM_HOME}/docker-compose.production.yml" ps | grep -q "${service}.*Up"; then
        echo "✓ ${service} está ejecutándose"
    else
        echo "✗ ${service} NO está ejecutándose"
        return 1
    fi
}

function backup_system() {
    local backup_dir="${SAAM_HOME}/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "${backup_dir}"
    
    echo "Creando backup en ${backup_dir}..."
    
    # Backup de base de datos
    docker-compose -f "${SAAM_HOME}/docker-compose.production.yml" exec postgres \
        pg_dump -U saam saam > "${backup_dir}/database.sql"
    
    # Backup de configuración
    cp -r "${SAAM_HOME}/config" "${backup_dir}/"
    
    # Backup de datos de memoria
    docker-compose -f "${SAAM_HOME}/docker-compose.production.yml" exec redis \
        redis-cli SAVE
    docker cp "$(docker-compose -f "${SAAM_HOME}/docker-compose.production.yml" ps -q redis)":/data/dump.rdb "${backup_dir}/redis.rdb"
    
    echo "Backup completado: ${backup_dir}"
}

function restore_system() {
    local backup_dir=$1
    
    if [[ -z "${backup_dir}" || ! -d "${backup_dir}" ]]; then
        echo "Directorio de backup no válido"
        return 1
    fi
    
    echo "Restaurando sistema desde ${backup_dir}..."
    stop_system
    
    # Restaurar base de datos
    docker-compose -f "${SAAM_HOME}/docker-compose.production.yml" start postgres
    sleep 5
    docker-compose -f "${SAAM_HOME}/docker-compose.production.yml" exec postgres \
        psql -U saam -d saam -f "${backup_dir}/database.sql"
    
    # Restaurar Redis
    docker-compose -f "${SAAM_HOME}/docker-compose.production.yml" start redis
    docker cp "${backup_dir}/redis.rdb" "$(docker-compose -f "${SAAM_HOME}/docker-compose.production.yml" ps -q redis)":/data/dump.rdb
    
    # Restaurar configuración
    cp -r "${backup_dir}/config" "${SAAM_HOME}/"
    
    start_system
    echo "Restauración completada"
}

# Manejo de comandos
case "$1" in
    start)
        start_system
        ;;
    stop)
        stop_system
        ;;
    restart)
        restart_system
        ;;
    status)
        check_system_status
        ;;
    backup)
        backup_system
        ;;
    restore)
        restore_system "$2"
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status|backup|restore}"
        exit 1
        ;;
esac