porqu#!/bin/bash
set -e

echo "Iniciando configuración personalizada de la base de datos..."

# Verificar si el archivo backup.sql existe
if [ -f "/docker-entrypoint-initdb.d/02-backup.sql" ]; then
    echo "Ejecutando backup.sql..."
    # Ejecutar el backup ignorando errores de DROP CONSTRAINT para tablas inexistentes
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=0 -f /docker-entrypoint-initdb.d/02-backup.sql
    echo "backup.sql ejecutado exitosamente."
else
    echo "Archivo backup.sql no encontrado. Saltando..."
fi

echo "Configuración de base de datos completada."