#!/usr/bin/env bash

# Proyecto Eficiencia Energética Chile - Startup Script
# Este script levanta toda la aplicación con Docker Compose

set -e  # Exit on any error

echo "🚀 Iniciando Proyecto Eficiencia Energética Chile..."
echo "================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker no está ejecutándose. Por favor inicia Docker Desktop."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose no está instalado."
    exit 1
fi

echo "✅ Docker está ejecutándose"

# Stop any existing containers
echo "🛑 Deteniendo contenedores existentes..."
docker-compose down 2>/dev/null || true

# Pull latest images
echo "📥 Descargando imágenes más recientes..."
docker-compose pull

# Build and start services
echo "🏗️  Construyendo y levantando servicios..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Esperando que los servicios estén listos..."
sleep 10

# Check service health
echo "🔍 Verificando estado de los servicios..."
docker-compose ps

echo ""
echo "🎉 ¡Aplicación iniciada exitosamente!"
echo "================================================"
echo "📱 API Principal: http://localhost:8000"
echo "🏥 Health Check: http://localhost:8000/health"
echo "🗄️  PostgreSQL: localhost:5432 (usuario: postgres)"
echo "🔴 Redis: localhost:6379"
echo ""
echo "📋 Comandos útiles:"
echo "   Ver logs: docker-compose logs -f"
echo "   Parar: docker-compose down"
echo "   Reiniciar: docker-compose restart"
echo ""
echo "📖 Para más información, consulta DOCKER_SETUP.md"

# Test the health endpoint
echo "🧪 Probando conectividad..."
sleep 5
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API respondiendo correctamente"
else
    echo "⚠️  API aún no responde, puede necesitar más tiempo para inicializar"
    echo "   Ejecuta: curl http://localhost:8000/health para verificar"
fi

echo ""
echo "🚀 ¡Listo para usar!"