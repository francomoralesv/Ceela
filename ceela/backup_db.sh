#!/bin/bash

# Script para hacer backup de la base de datos PostgreSQL
# Guarda el backup con la fecha actual en el nombre del archivo

# Configuración de la base de datos (desde docker-compose.yml)
DB_NAME="energy_efficiency"
DB_USER="postgres"
DB_PASSWORD="vgBwQe77JCblzJFM"
DB_HOST="localhost"
DB_PORT="15432"
CONTAINER_NAME="ceela-postgres"

# Directorio donde se guardarán los backups
BACKUP_DIR="./backups"

# Crear directorio de backups si no existe
mkdir -p "$BACKUP_DIR"

# Obtener la fecha actual en formato YYYYMMDD_HHMMSS
CURRENT_DATE=$(date +"%Y%m%d_%H%M%S")

# Nombre del archivo de backup
BACKUP_FILE="$BACKUP_DIR/backup_${CURRENT_DATE}.sql"

echo "======================================"
echo "Iniciando backup de la base de datos"
echo "======================================"
echo "Base de datos: $DB_NAME"
echo "Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Archivo: $BACKUP_FILE"
echo ""

# Verificar si el contenedor está corriendo
if docker ps | grep -q "$CONTAINER_NAME"; then
    echo "✓ Contenedor PostgreSQL encontrado"

    # Opción 1: Hacer backup usando docker exec (recomendado cuando se usa Docker)
    echo "Generando backup..."
    docker exec -t "$CONTAINER_NAME" pg_dump -U "$DB_USER" -d "$DB_NAME" --clean --if-exists > "$BACKUP_FILE"

    # Verificar si el backup fue exitoso
    if [ $? -eq 0 ]; then
        # Obtener el tamaño del archivo
        BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        echo ""
        echo "✓ Backup completado exitosamente"
        echo "  Tamaño: $BACKUP_SIZE"
        echo "  Ubicación: $BACKUP_FILE"
        echo ""

        # Listar backups existentes
        echo "Backups disponibles:"
        ls -lh "$BACKUP_DIR"/backup_*.sql 2>/dev/null | awk '{print "  -", $9, "("$5")"}'

        # Opcional: Eliminar backups antiguos (más de 30 días)
        # Descomentar la siguiente línea si deseas mantener solo los backups de los últimos 30 días
        # find "$BACKUP_DIR" -name "backup_*.sql" -type f -mtime +30 -delete

        exit 0
    else
        echo "✗ Error al generar el backup"
        exit 1
    fi
else
    echo "✗ El contenedor PostgreSQL no está corriendo"
    echo ""
    echo "Por favor, inicia el contenedor con:"
    echo "  docker-compose up -d postgres"
    echo ""
    echo "O usa la conexión directa si PostgreSQL está instalado localmente:"
    echo "  PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME --clean --if-exists > $BACKUP_FILE"
    exit 1
fi
