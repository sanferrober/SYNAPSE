# Despliegue de Synapse con Docker

Este documento describe cu00f3mo desplegar Synapse utilizando Docker y Docker Compose.

## Requisitos previos

- Docker instalado (versiu00f3n 19.03.0+)
- Docker Compose instalado (versiu00f3n 1.27.0+)

## Estructura de archivos

- `Dockerfile.backend`: Configuraciu00f3n para construir la imagen del backend
- `Dockerfile.frontend`: Configuraciu00f3n para construir la imagen del frontend para producciu00f3n
- `Dockerfile.frontend.dev`: Configuraciu00f3n para construir la imagen del frontend para desarrollo
- `docker-compose.yml`: Configuraciu00f3n para orquestar los servicios en producciu00f3n
- `docker-compose.dev.yml`: Configuraciu00f3n para orquestar los servicios en desarrollo
- `deploy.sh`: Script para facilitar el despliegue en producciu00f3n
- `deploy-dev.sh`: Script para facilitar el despliegue en desarrollo
- `nginx.conf`: Configuraciu00f3n de Nginx para el frontend en producciu00f3n

## Pasos para el despliegue

### Despliegue en producciu00f3n

#### Opciu00f3n 1: Usando el script de despliegue

1. Dar permisos de ejecuciu00f3n al script:
   ```bash
   chmod +x deploy.sh
   ```

2. Ejecutar el script:
   ```bash
   ./deploy.sh
   ```

#### Opciu00f3n 2: Despliegue manual

1. Construir y levantar los contenedores:
   ```bash
   docker-compose up -d --build
   ```

2. Verificar que los contenedores estu00e1n en ejecuciu00f3n:
   ```bash
   docker-compose ps
   ```

### Despliegue en desarrollo

#### Opciu00f3n 1: Usando el script de despliegue para desarrollo

1. Dar permisos de ejecuciu00f3n al script:
   ```bash
   chmod +x deploy-dev.sh
   ```

2. Ejecutar el script:
   ```bash
   ./deploy-dev.sh
   ```

#### Opciu00f3n 2: Despliegue manual para desarrollo

1. Construir y levantar los contenedores:
   ```bash
   docker-compose -f docker-compose.dev.yml up -d --build
   ```

2. Verificar que los contenedores estu00e1n en ejecuciu00f3n:
   ```bash
   docker-compose -f docker-compose.dev.yml ps
   ```

## Acceso a la aplicaciu00f3n

### Producciu00f3n
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

### Desarrollo
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## Detener la aplicaciu00f3n

### Producciu00f3n
```bash
docker-compose down
```

### Desarrollo
```bash
docker-compose -f docker-compose.dev.yml down
```

## Logs

### Producciu00f3n
```bash
# Ver logs de todos los servicios
docker-compose logs

# Ver logs del backend
docker-compose logs backend

# Ver logs del frontend
docker-compose logs frontend

# Ver logs en tiempo real
docker-compose logs -f
```

### Desarrollo
```bash
# Ver logs de todos los servicios
docker-compose -f docker-compose.dev.yml logs

# Ver logs del backend
docker-compose -f docker-compose.dev.yml logs backend

# Ver logs del frontend
docker-compose -f docker-compose.dev.yml logs frontend

# Ver logs en tiempo real
docker-compose -f docker-compose.dev.yml logs -f
```

## Persistencia de datos

Los siguientes archivos se mantienen persistentes entre reinicios:

- `synapse_memory.json`: Almacena la memoria del sistema
- `llm_config.json`: Almacena la configuraciu00f3n de los LLMs

## Diferencias entre producciu00f3n y desarrollo

### Producciu00f3n
- El frontend se construye como una aplicaciu00f3n estu00e1tica y se sirve con Nginx
- El backend se ejecuta en modo producciu00f3n
- No hay montaje de volu00famenes para el cu00f3digo fuente (solo para archivos de datos)

### Desarrollo
- El frontend se ejecuta con el servidor de desarrollo de React (hot-reloading)
- El backend se ejecuta en modo desarrollo con recarga autu00f3matica
- Se montan volu00famenes para el cu00f3digo fuente, permitiendo editar el cu00f3digo en tiempo real

## Soluciones a problemas comunes

### El frontend no puede conectarse al backend

Verifique que el backend estu00e1 en ejecuciu00f3n y accesible:

```bash
curl http://localhost:5000/api/health
```

### Problemas de permisos con los archivos de persistencia

Si hay problemas de permisos con los archivos de persistencia, puede cambiar los permisos:

```bash
chmod 666 synapse_memory.json llm_config.json
```

### Problemas con los volu00famenes en modo desarrollo

Si hay problemas con los volu00famenes en modo desarrollo, puede intentar reconstruir los contenedores:

```bash
docker-compose -f docker-compose.dev.yml down -v
docker-compose -f docker-compose.dev.yml up -d --build
```