#!/bin/bash

# Script para crear snapshot completo del proyecto con datos
# Autor: Sistema de migración automatizada
# Fecha: $(date)

set -e  # Salir si hay errores

echo "🚀 Iniciando creación de snapshot completo..."

# Variables
PROJECT_NAME="proyecto_eficiencia_energetica_chile"
SNAPSHOT_DIR="snapshot_$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="$SNAPSHOT_DIR/data_backup"
CURRENT_DIR=$(pwd)

# Crear directorio temporal para el snapshot
echo "📁 Creando directorio de snapshot: $SNAPSHOT_DIR"
mkdir -p "$SNAPSHOT_DIR"
mkdir -p "$BACKUP_DIR"

# 1. Copiar archivos del proyecto (excluyendo datos temporales)
echo "📋 Copiando archivos del proyecto..."
rsync -av --progress \
  --exclude='node_modules' \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.pytest_cache' \
  --exclude='logs' \
  --exclude='tmp' \
  --exclude="$SNAPSHOT_DIR" \
  . "$SNAPSHOT_DIR/"

# 2. Verificar que Docker Compose esté ejecutándose
echo "🐳 Verificando estado de contenedores..."
if ! docker-compose ps | grep -q "Up"; then
    echo "⚠️  Advertencia: Algunos contenedores no están ejecutándose"
    echo "   Iniciando contenedores para backup..."
    docker-compose up -d
    sleep 10
fi

# 3. Backup de base de datos PostgreSQL
echo "🗄️  Creando backup de PostgreSQL..."
docker-compose exec -T postgres pg_dumpall -c -U postgres > "$BACKUP_DIR/postgres_backup.sql"
echo "   ✅ Backup de PostgreSQL completado"

# 4. Backup de datos de Redis
echo "📊 Creando backup de Redis..."
docker-compose exec -T redis redis-cli --rdb /data/dump.rdb BGSAVE
sleep 5
docker cp $(docker-compose ps -q redis):/data/dump.rdb "$BACKUP_DIR/redis_dump.rdb"
echo "   ✅ Backup de Redis completado"

# 5. Backup de volúmenes de datos de contenedores Docker
echo "📦 Creando backup de volúmenes de contenedores..."

# Backup de archivos públicos desde el contenedor app
echo "   📁 Respaldando archivos públicos desde contenedor..."
docker-compose exec -T app tar -czf - -C / app/public 2>/dev/null > "$BACKUP_DIR/public_data.tar.gz" || \
docker-compose exec -T app tar -czf - -C / public 2>/dev/null > "$BACKUP_DIR/public_data.tar.gz" || \
echo "   ⚠️  No se encontraron archivos públicos en el contenedor"

# Backup de volúmenes Docker nombrados
echo "   📦 Respaldando volúmenes Docker..."
for volume in $(docker volume ls --format "{{.Name}}" | grep "$(basename $PWD)"); do
    echo "   📝 Respaldando volumen: $volume"
    docker run --rm -v "$volume:/source" -v "$CURRENT_DIR/$BACKUP_DIR:/backup" alpine tar -czf "/backup/volume_${volume##*/}.tar.gz" -C /source . 2>/dev/null || echo "   ⚠️  Error respaldando $volume"
done

# Backup de archivos de aplicación desde contenedor
echo "   📄 Respaldando archivos de aplicación desde contenedor..."
docker-compose exec -T app tar -czf - -C / app/uploads 2>/dev/null > "$BACKUP_DIR/app_uploads.tar.gz" || \
echo "   ⚠️  No se encontraron uploads en el contenedor"

# 6. Crear archivo de configuración para restauración
echo "⚙️  Creando archivo de configuración..."
cat > "$SNAPSHOT_DIR/restore_config.env" << EOF
# Configuración para restauración del snapshot
# Generado automáticamente el $(date)

SNAPSHOT_VERSION=$(date +%Y%m%d_%H%M%S)
ORIGINAL_SERVER=$(hostname)
BACKUP_DATE=$(date)
PROJECT_NAME=$PROJECT_NAME

# Archivos de backup incluidos (desde contenedores Docker)
POSTGRES_BACKUP=data_backup/postgres_backup.sql
REDIS_BACKUP=data_backup/redis_dump.rdb
PUBLIC_DATA=data_backup/public_data.tar.gz
APP_UPLOADS=data_backup/app_uploads.tar.gz
DOCKER_VOLUMES=data_backup/volume_*.tar.gz
EOF

# 7. Crear script de restauración
echo "🔧 Creando script de restauración..."
cat > "$SNAPSHOT_DIR/restore.sh" << 'EOF'
#!/bin/bash

# Script de restauración automática
# Ejecutar en el servidor destino

set -e

echo "🔄 Iniciando restauración del snapshot..."

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Error: No se encuentra docker-compose.yml"
    echo "   Asegúrate de estar en el directorio del proyecto"
    exit 1
fi

# Cargar configuración
if [ -f "restore_config.env" ]; then
    source restore_config.env
    echo "📋 Configuración cargada: Snapshot $SNAPSHOT_VERSION"
else
    echo "⚠️  Archivo de configuración no encontrado, continuando..."
fi

# Detener contenedores existentes
echo "🛑 Deteniendo contenedores existentes..."
docker-compose down -v

# Iniciar solo la base de datos para restauración
echo "🗄️  Iniciando PostgreSQL para restauración..."
docker-compose up -d postgres
sleep 10

# Restaurar base de datos
if [ -f "data_backup/postgres_backup.sql" ]; then
    echo "📥 Restaurando base de datos PostgreSQL..."
    docker-compose exec -T postgres psql -U postgres < data_backup/postgres_backup.sql
    echo "   ✅ Base de datos restaurada"
else
    echo "⚠️  No se encontró backup de PostgreSQL"
fi

# Iniciar Redis
echo "📊 Iniciando Redis..."
docker-compose up -d redis
sleep 5

# Restaurar datos de Redis
if [ -f "data_backup/redis_dump.rdb" ]; then
    echo "📥 Restaurando datos de Redis..."
    docker cp data_backup/redis_dump.rdb $(docker-compose ps -q redis):/data/dump.rdb
    docker-compose restart redis
    echo "   ✅ Datos de Redis restaurados"
else
    echo "⚠️  No se encontró backup de Redis"
fi

# Iniciar contenedor de aplicación para restaurar archivos
echo "🚀 Iniciando contenedor de aplicación..."
docker-compose up -d app
sleep 10

# Restaurar archivos públicos al contenedor
if [ -f "data_backup/public_data.tar.gz" ]; then
    echo "📁 Restaurando archivos públicos al contenedor..."
    docker-compose exec -T app mkdir -p /app/public /public
    cat data_backup/public_data.tar.gz | docker-compose exec -T app tar -xzf - -C /
    echo "   ✅ Archivos públicos restaurados al contenedor"
else
    echo "⚠️  No se encontró backup de archivos públicos"
fi

# Restaurar uploads al contenedor
if [ -f "data_backup/app_uploads.tar.gz" ]; then
    echo "📄 Restaurando uploads al contenedor..."
    docker-compose exec -T app mkdir -p /app/uploads
    cat data_backup/app_uploads.tar.gz | docker-compose exec -T app tar -xzf - -C /
    echo "   ✅ Uploads restaurados al contenedor"
else
    echo "⚠️  No se encontró backup de uploads"
fi

# Restaurar volúmenes Docker
echo "📦 Restaurando volúmenes Docker..."
for volume_backup in data_backup/volume_*.tar.gz; do
    if [ -f "$volume_backup" ]; then
        volume_name=$(basename "$volume_backup" .tar.gz | sed 's/volume_//')
        full_volume_name="${PWD##*/}_${volume_name}"
        echo "   📝 Restaurando volumen: $full_volume_name"
        docker volume create "$full_volume_name" 2>/dev/null || true
        docker run --rm -v "$full_volume_name:/target" -v "$(pwd)/data_backup:/backup" alpine tar -xzf "/backup/$(basename $volume_backup)" -C /target
        echo "   ✅ Volumen $full_volume_name restaurado"
    fi
done

# Iniciar todos los servicios
echo "🚀 Iniciando todos los servicios..."
docker-compose up --build -d

# Verificar estado
echo "🔍 Verificando estado de los servicios..."
sleep 10
docker-compose ps

echo "✅ Restauración completada!"
echo "📋 Verifica que todos los servicios estén funcionando correctamente"
echo "🌐 La aplicación debería estar disponible según tu configuración"
EOF

chmod +x "$SNAPSHOT_DIR/restore.sh"

# 8. Crear archivo README con instrucciones
echo "📖 Creando documentación..."
cat > "$SNAPSHOT_DIR/README_MIGRACION.md" << EOF
# Snapshot de Migración - $PROJECT_NAME

**Fecha de creación:** $(date)  
**Servidor origen:** $(hostname)  
**Versión:** $(date +%Y%m%d_%H%M%S)

## Contenido del Snapshot

- ✅ Código fuente completo del proyecto
- ✅ Configuración Docker (docker-compose.yml)
- ✅ Variables de entorno (.env)
- ✅ Backup completo de PostgreSQL (desde contenedor)
- ✅ Backup de datos Redis (desde contenedor)
- ✅ Archivos públicos y uploads (desde contenedores)
- ✅ Volúmenes Docker nombrados
- ✅ Script de restauración automatizada

## Instrucciones de Migración

### 1. Transferir al servidor destino
\`\`\`bash
# Comprimir el snapshot
tar -czf ${SNAPSHOT_DIR}.tar.gz $SNAPSHOT_DIR/

# Transferir al servidor destino (ejemplo con scp)
scp ${SNAPSHOT_DIR}.tar.gz usuario@servidor-destino:/ruta/destino/
\`\`\`

### 2. En el servidor destino
\`\`\`bash
# Extraer el snapshot
tar -xzf ${SNAPSHOT_DIR}.tar.gz
cd $SNAPSHOT_DIR

# Ejecutar restauración automática
./restore.sh
\`\`\`

### 3. Verificación post-migración
\`\`\`bash
# Verificar contenedores
docker-compose ps

# Verificar logs
docker-compose logs -f app

# Verificar conectividad de base de datos
docker-compose exec app env | grep DB_CONNECTION
\`\`\`

## Notas Importantes

- 🔧 Ajusta las variables de entorno en .env según el nuevo servidor
- 🌐 Configura puertos y firewall según sea necesario
- 🔒 Verifica que las credenciales y API keys sean correctas
- 📊 El backup incluye todos los datos hasta: $(date)

## Solución de Problemas

### Si hay errores de permisos:
\`\`\`bash
sudo chown -R \$USER:\$USER .
chmod +x restore.sh
\`\`\`

### Si fallan los contenedores:
\`\`\`bash
docker-compose down -v
docker-compose up --build -d
\`\`\`

### Para verificar datos:
\`\`\`bash
# Verificar PostgreSQL
docker-compose exec postgres psql -U postgres -c "\\l"

# Verificar Redis
docker-compose exec redis redis-cli ping
\`\`\`
EOF

# 9. Comprimir todo el snapshot
echo "🗜️  Comprimiendo snapshot..."
tar -czf "${SNAPSHOT_DIR}.tar.gz" "$SNAPSHOT_DIR/"

# 10. Mostrar resumen
echo ""
echo "✅ ¡Snapshot creado exitosamente!"
echo ""
echo "📦 Archivo de snapshot: ${SNAPSHOT_DIR}.tar.gz"
echo "📊 Tamaño: $(du -h "${SNAPSHOT_DIR}.tar.gz" | cut -f1)"
echo ""
echo "📋 Contenido incluido (desde contenedores Docker):"
echo "   - Código fuente completo"
echo "   - Backup de PostgreSQL ($(du -h "$BACKUP_DIR/postgres_backup.sql" 2>/dev/null | cut -f1 || echo 'N/A'))"
echo "   - Backup de Redis ($(du -h "$BACKUP_DIR/redis_dump.rdb" 2>/dev/null | cut -f1 || echo 'N/A'))"
echo "   - Archivos públicos de contenedores ($(du -h "$BACKUP_DIR/public_data.tar.gz" 2>/dev/null | cut -f1 || echo 'N/A'))"
echo "   - Uploads de contenedores ($(du -h "$BACKUP_DIR/app_uploads.tar.gz" 2>/dev/null | cut -f1 || echo 'N/A'))"
echo "   - Volúmenes Docker nombrados"
echo "   - Script de restauración automática"
echo ""
echo "🚀 Para migrar:"
echo "   1. Transferir: scp ${SNAPSHOT_DIR}.tar.gz usuario@servidor:/destino/"
echo "   2. Extraer: tar -xzf ${SNAPSHOT_DIR}.tar.gz"
echo "   3. Restaurar: cd $SNAPSHOT_DIR && ./restore.sh"
echo ""
echo "📖 Lee README_MIGRACION.md para instrucciones detalladas"

# Limpiar directorio temporal (opcional)
read -p "¿Deseas eliminar el directorio temporal $SNAPSHOT_DIR? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$SNAPSHOT_DIR"
    echo "🗑️  Directorio temporal eliminado"
fi

echo ""
echo "🎉 ¡Proceso completado!"