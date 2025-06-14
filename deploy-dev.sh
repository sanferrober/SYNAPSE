#!/bin/bash

# Script para desplegar Synapse en modo desarrollo con Docker

echo "=== Desplegando Synapse en modo desarrollo con Docker ==="

# Verificar si Docker estu00e1 instalado
if ! command -v docker &> /dev/null; then
    echo "Error: Docker no estu00e1 instalado. Por favor, instale Docker antes de continuar."
    exit 1
fi

# Verificar si Docker Compose estu00e1 instalado
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose no estu00e1 instalado. Por favor, instale Docker Compose antes de continuar."
    exit 1
fi

# Construir y levantar los contenedores
echo "Construyendo y levantando los contenedores en modo desarrollo..."
docker-compose -f docker-compose.dev.yml up -d --build

# Verificar si los contenedores estu00e1n en ejecuciu00f3n
if [ $(docker-compose -f docker-compose.dev.yml ps -q | wc -l) -eq 2 ]; then
    echo "=== Synapse se ha desplegado correctamente en modo desarrollo ==="
    echo "Backend: http://localhost:5000"
    echo "Frontend: http://localhost:3000"
    echo "Para ver los logs en tiempo real, ejecute: docker-compose -f docker-compose.dev.yml logs -f"
    echo "Para detener los servicios, ejecute: docker-compose -f docker-compose.dev.yml down"
else
    echo "Error: Hubo un problema al desplegar Synapse. Revise los logs con: docker-compose -f docker-compose.dev.yml logs"
    exit 1
fi