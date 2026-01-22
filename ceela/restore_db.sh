#!/bin/bash

# Script para restaurar la base de datos PostgreSQL desde un backup
# Uso: ./restore_db.sh <archivo_backup.sql>

# Configuración de la base de datos
DB_NAME="energy_efficiency"
DB_USER="postgres"
DB_PASSWORD="vgBwQe77JCblzJFM"
DB_HOST="localhost"
DB_PORT="15432"
CONTAINER_NAME="ceela-postgres"

# Directorio de backups
BACKUP_DIR="./backups"

# Función para mostrar uso
show_usage() {
    echo "Uso: $0 [archivo_backup.sql]"
    echo ""
    echo "Si no se especifica un archivo, se mostrará una lista de backups disponibles"
    echo ""
    echo "Ejemplos:"
    echo "  $0 backups/backup_20250110_120000.sql"
    echo "  $0  (para ver lista de backups disponibles)"
}

# Función para listar backups disponibles
list_backups() {
    echo "Backups disponibles:"
    echo ""
    ls -lht "$BACKUP_DIR"/backup_*.sql 2>/dev/null | awk '{
        # Extraer nombre del archivo
        file = $9
        # Extraer fecha del nombre del archivo
        split(file, parts, "_")
        if (length(parts) >= 3) {
            date_part = parts[2]
            time_part = parts[3]
            gsub(".sql", "", time_part)

            # Formatear fecha
            year = substr(date_part, 1, 4)
            month = substr(date_part, 5, 2)
            day = substr(date_part, 7, 2)
            hour = substr(time_part, 1, 2)
            min = substr(time_part, 3, 2)
            sec = substr(time_part, 5, 2)

            printf "  %2d) %s\n      Fecha: %s-%s-%s %s:%s:%s\n      Tamaño: %s\n\n",
                   NR, file, year, month, day, hour, min, sec, $5
        }
    }'
}

# Verificar si el contenedor está corriendo
check_container() {
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        echo "✗ El contenedor PostgreSQL no está corriendo"
        echo ""
        echo "Por favor, inicia el contenedor con:"
        echo "  docker-compose up -d postgres"
        exit 1
    fi
    echo "✓ Contenedor PostgreSQL encontrado"
}

# Restaurar backup
restore_backup() {
    local backup_file=$1

    if [ ! -f "$backup_file" ]; then
        echo "✗ Error: El archivo '$backup_file' no existe"
        exit 1
    fi

    echo "======================================"
    echo "Restaurando backup de la base de datos"
    echo "======================================"
    echo "Archivo: $backup_file"
    echo "Base de datos: $DB_NAME"
    echo "Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""

    # Advertencia
    echo "⚠️  ADVERTENCIA: Esta operación eliminará todos los datos actuales en la base de datos"
    echo ""
    read -p "¿Estás seguro de que deseas continuar? (sí/no): " confirm

    if [ "$confirm" != "sí" ] && [ "$confirm" != "si" ] && [ "$confirm" != "yes" ]; then
        echo "Restauración cancelada"
        exit 0
    fi

    echo ""
    echo "Restaurando datos..."

    # Restaurar usando docker exec
    docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" < "$backup_file"

    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Backup restaurado exitosamente"
        exit 0
    else
        echo ""
        echo "✗ Error al restaurar el backup"
        exit 1
    fi
}

# Programa principal
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    show_usage
    exit 0
fi

check_container

if [ -z "$1" ]; then
    # Si no se proporciona archivo, mostrar lista
    list_backups
    echo ""
    read -p "Ingresa el número o nombre del archivo a restaurar (o 'q' para salir): " selection

    if [ "$selection" == "q" ] || [ -z "$selection" ]; then
        echo "Operación cancelada"
        exit 0
    fi

    # Si es un número, obtener el archivo correspondiente
    if [[ "$selection" =~ ^[0-9]+$ ]]; then
        backup_file=$(ls -t "$BACKUP_DIR"/backup_*.sql 2>/dev/null | sed -n "${selection}p")
        if [ -z "$backup_file" ]; then
            echo "✗ Selección inválida"
            exit 1
        fi
    else
        backup_file="$selection"
    fi

    restore_backup "$backup_file"
else
    restore_backup "$1"
fi
