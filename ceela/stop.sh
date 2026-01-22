#!/bin/bash

# Proyecto Eficiencia Energética Chile - Stop Script
# Este script detiene todos los servicios de Docker Compose

set -e  # Exit on any error

echo "🛑 Deteniendo Proyecto Eficiencia Energética Chile..."
echo "================================================"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose no está instalado."
    exit 1
fi

# Stop all services
echo "🔄 Deteniendo todos los servicios..."
docker-compose down

echo "✅ Todos los servicios han sido detenidos"
echo ""
echo "💡 Comandos adicionales:"
echo "   Eliminar también volúmenes: docker-compose down -v"
echo "   Ver contenedores: docker-compose ps"
echo "   Reiniciar: ./start.sh"
echo ""
echo "🏁 ¡Aplicación detenida!"