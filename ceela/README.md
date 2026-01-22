# Proyecto Eficiencia Energetica Chile Backend

API para proyecto de eficiencia energética Chile.

## Descripción

Este proyecto es una API desarrollada en Python utilizando el framework FastAPI. La API permite gestionar usuarios, autenticación, proyectos y constantes relacionadas con la eficiencia energética en Chile.

## 🚀 Despliegue Automatizado con Docker (Recomendado)

### 📋 Requisitos del Servidor

Para desplegar este proyecto en un servidor, necesitas:

#### Requisitos Obligatorios:
- **Docker Engine** (versión 20.10 o superior)
  - Para instalación en servidor: `curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh`
  - Alternativamente, usar el gestor de paquetes del sistema
- **Docker Compose** v2.0+ 
  - Instalación: `sudo apt-get install docker-compose-plugin` (Ubuntu/Debian)
  - O descargar desde: https://github.com/docker/compose/releases
- **4GB RAM mínimo** (16GB recomendado para producción)
- **10GB de espacio libre en disco** (para imágenes, volúmenes y logs)

#### Especificaciones del Servidor:
- **Sistema Operativo**: Linux (Ubuntu 20.04+, CentOS 8+, RHEL 8+, Debian 11+)
- **Arquitectura**: x86_64 (AMD64)
- **CPU**: 2 cores mínimo (4 cores recomendado)
- **Conexión a Internet** estable (para descargas y APIs externas)
- **Puertos disponibles**: 8000, 3000, 5432, 6379

#### Configuración Adicional:
- **Firewall**: Configurar puertos necesarios
- **Usuario con privilegios sudo** para instalación de Docker
- **Certificados SSL** (recomendado para producción)

> ⚠️ **Importante**: Asegúrate de que el servicio Docker esté iniciado: `sudo systemctl start docker && sudo systemctl enable docker`

### 🔑 Configuración de Variables de Entorno

Antes del despliegue, debes configurar las siguientes variables de entorno en el archivo `docker-compose.yml`:

**Para el servicio frontend (líneas 54-55):**
```yaml
environment:
  AWS_PLACE_INDEX_NAME: CeelaIndex
  PLACES_API_KEY: "tu_api_key_aqui"
```

**Para el servicio backend (líneas 61-62 y 79-80):**
```yaml
environment:
  - PLACES_API_KEY=tu_api_key_aqui
  - AWS_PLACE_INDEX_NAME=CeelaIndex
```

> ⚠️ **Importante**: Las claves proporcionadas en el repositorio son temporales. Debes obtener tu propia `PLACES_API_KEY` para uso en producción y editarla directamente en el archivo `docker-compose.yml`.

#### 🔗 Enlaces útiles para configurar AWS Location Service

Para crear y configurar correctamente los servicios de AWS necesarios:

• **Crear un PlaceIndex**  
  [CreatePlaceIndex API Reference](https://docs.aws.amazon.com/location/latest/APIReference/API_CreatePlaceIndex.html)

• **Crear una API key para Amazon Location Service**  
  [Use API keys to authenticate - Amazon Location Service](https://docs.aws.amazon.com/location/latest/developerguide/using-apikeys.html)

• **Comando CLI para crear PlaceIndex**  
  [AWS CLI create-place-index](https://docs.aws.amazon.com/cli/latest/reference/location/create-place-index.html)

> 💡 **Tip**: Asegúrate de que tu PlaceIndex tenga el nombre `CeelaIndex` o actualiza la variable `AWS_PLACE_INDEX_NAME` en el docker-compose.yml con el nombre que elijas.

### ⚡ Despliegue Completo (Un Solo Comando)
```bash
docker-compose up --build -d
```

Este comando único:
- ✅ Construye todas las imágenes necesarias
- ✅ Inicializa PostgreSQL con backup.sql automáticamente (42 tablas + datos)
- ✅ Levanta el backend FastAPI
- ✅ Levanta el frontend Next.js
- ✅ Configura toda la red y volúmenes

### 🌐 URLs de acceso
- **API Principal**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Health Check**: http://localhost:8000/health
- **Temporal UI**: http://localhost:8080
- **PostgreSQL**: localhost:5432 (usuario: postgres, db: energy_efficiency)

### 🛑 Parar la aplicación
```bash
# Parar todos los servicios
docker-compose down

# Parar y limpiar volúmenes (reinicio completo)
docker-compose down -v
```

### 🔧 Comandos útiles
```bash
# Ver estado de los servicios
docker-compose ps

# Ver logs de todos los servicios
docker-compose logs

# Ver logs específicos
docker-compose logs postgres
docker-compose logs backend
docker-compose logs frontend

# Reconstruir solo un servicio
docker-compose up --build postgres -d
```

## 🗄️ Base de Datos Automatizada

La base de datos PostgreSQL se inicializa automáticamente con:
- **42 tablas** creadas desde backup.sql
- **Datos de prueba** incluidos
- **Sin configuración manual** requerida

### Archivos de automatización:
- `Dockerfile.postgres` - Imagen personalizada de PostgreSQL
- `init-db.sh` - Script de inicialización automática
- `backup.sql` - Dump completo de la base de datos

---

## 🚀 Despliegue en Servidor

### Método Automatizado (Recomendado)
```bash
# En el servidor, ejecutar:
unzip ceelacompilado.zip
cd ceela
chmod -x start.sh
./start.sh
```


## 📁 Estructura del Proyecto

```
ceela/
├── src/                    # Código fuente del backend
├── frontend/              # Aplicación Next.js
├── docker-compose.yml     # Configuración de servicios
├── Dockerfile.postgres    # Imagen personalizada PostgreSQL
├── init-db.sh            # Script de inicialización DB
├── backup.sql            # Dump de base de datos
└── requirements.txt      # Dependencias Python
```