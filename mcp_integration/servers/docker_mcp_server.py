"""
Servidor MCP para Docker - Integración con Synapse

Este servidor MCP proporciona herramientas para gestionar contenedores Docker,
imágenes, volúmenes y redes desde Synapse.
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

import docker
from docker.errors import DockerException, NotFound, APIError
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult
)

logger = logging.getLogger(__name__)

@dataclass
class DockerConfig:
    """Configuración para el servidor Docker MCP"""
    base_url: str = "unix://var/run/docker.sock"
    timeout: int = 60
    version: str = "auto"

class DockerMCPServer:
    """Servidor MCP para integración con Docker"""
    
    def __init__(self, config: DockerConfig):
        self.config = config
        self.server = Server("docker-mcp-server")
        
        try:
            self.client = docker.DockerClient(
                base_url=config.base_url,
                timeout=config.timeout,
                version=config.version
            )
            # Verificar conexión
            self.client.ping()
            logger.info("Conexión a Docker establecida exitosamente")
        except DockerException as e:
            logger.error(f"Error conectando a Docker: {e}")
            self.client = None
        
        self._register_tools()
    
    def _register_tools(self):
        """Registra todas las herramientas disponibles"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """Lista todas las herramientas disponibles"""
            tools = [
                Tool(
                    name="docker_list_containers",
                    description="Lista contenedores Docker",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "all": {
                                "type": "boolean",
                                "description": "Incluir contenedores detenidos",
                                "default": False
                            },
                            "filters": {
                                "type": "object",
                                "description": "Filtros para aplicar (ej: {'status': 'running'})"
                            }
                        }
                    }
                ),
                Tool(
                    name="docker_get_container",
                    description="Obtiene información detallada de un contenedor",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "container_id": {
                                "type": "string",
                                "description": "ID o nombre del contenedor"
                            }
                        },
                        "required": ["container_id"]
                    }
                ),
                Tool(
                    name="docker_start_container",
                    description="Inicia un contenedor",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "container_id": {
                                "type": "string",
                                "description": "ID o nombre del contenedor"
                            }
                        },
                        "required": ["container_id"]
                    }
                ),
                Tool(
                    name="docker_stop_container",
                    description="Detiene un contenedor",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "container_id": {
                                "type": "string",
                                "description": "ID o nombre del contenedor"
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Tiempo de espera en segundos",
                                "default": 10
                            }
                        },
                        "required": ["container_id"]
                    }
                ),
                Tool(
                    name="docker_restart_container",
                    description="Reinicia un contenedor",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "container_id": {
                                "type": "string",
                                "description": "ID o nombre del contenedor"
                            },
                            "timeout": {
                                "type": "integer",
                                "description": "Tiempo de espera en segundos",
                                "default": 10
                            }
                        },
                        "required": ["container_id"]
                    }
                ),
                Tool(
                    name="docker_remove_container",
                    description="Elimina un contenedor",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "container_id": {
                                "type": "string",
                                "description": "ID o nombre del contenedor"
                            },
                            "force": {
                                "type": "boolean",
                                "description": "Forzar eliminación de contenedor en ejecución",
                                "default": False
                            },
                            "v": {
                                "type": "boolean",
                                "description": "Eliminar volúmenes asociados",
                                "default": False
                            }
                        },
                        "required": ["container_id"]
                    }
                ),
                Tool(
                    name="docker_run_container",
                    description="Ejecuta un nuevo contenedor",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "image": {
                                "type": "string",
                                "description": "Imagen Docker a ejecutar"
                            },
                            "command": {
                                "type": "string",
                                "description": "Comando a ejecutar en el contenedor"
                            },
                            "name": {
                                "type": "string",
                                "description": "Nombre para el contenedor"
                            },
                            "ports": {
                                "type": "object",
                                "description": "Mapeo de puertos (ej: {'80/tcp': 8080})"
                            },
                            "environment": {
                                "type": "object",
                                "description": "Variables de entorno"
                            },
                            "volumes": {
                                "type": "object",
                                "description": "Mapeo de volúmenes"
                            },
                            "detach": {
                                "type": "boolean",
                                "description": "Ejecutar en segundo plano",
                                "default": True
                            },
                            "remove": {
                                "type": "boolean",
                                "description": "Eliminar contenedor al terminar",
                                "default": False
                            }
                        },
                        "required": ["image"]
                    }
                ),
                Tool(
                    name="docker_list_images",
                    description="Lista imágenes Docker",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "all": {
                                "type": "boolean",
                                "description": "Incluir imágenes intermedias",
                                "default": False
                            },
                            "filters": {
                                "type": "object",
                                "description": "Filtros para aplicar"
                            }
                        }
                    }
                ),
                Tool(
                    name="docker_pull_image",
                    description="Descarga una imagen Docker",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "repository": {
                                "type": "string",
                                "description": "Repositorio de la imagen"
                            },
                            "tag": {
                                "type": "string",
                                "description": "Tag de la imagen",
                                "default": "latest"
                            }
                        },
                        "required": ["repository"]
                    }
                ),
                Tool(
                    name="docker_remove_image",
                    description="Elimina una imagen Docker",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "image": {
                                "type": "string",
                                "description": "ID o nombre de la imagen"
                            },
                            "force": {
                                "type": "boolean",
                                "description": "Forzar eliminación",
                                "default": False
                            }
                        },
                        "required": ["image"]
                    }
                ),
                Tool(
                    name="docker_get_logs",
                    description="Obtiene logs de un contenedor",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "container_id": {
                                "type": "string",
                                "description": "ID o nombre del contenedor"
                            },
                            "tail": {
                                "type": "integer",
                                "description": "Número de líneas desde el final",
                                "default": 100
                            },
                            "follow": {
                                "type": "boolean",
                                "description": "Seguir logs en tiempo real",
                                "default": False
                            },
                            "timestamps": {
                                "type": "boolean",
                                "description": "Incluir timestamps",
                                "default": True
                            }
                        },
                        "required": ["container_id"]
                    }
                ),
                Tool(
                    name="docker_exec_command",
                    description="Ejecuta un comando en un contenedor en ejecución",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "container_id": {
                                "type": "string",
                                "description": "ID o nombre del contenedor"
                            },
                            "command": {
                                "type": "string",
                                "description": "Comando a ejecutar"
                            },
                            "workdir": {
                                "type": "string",
                                "description": "Directorio de trabajo"
                            },
                            "user": {
                                "type": "string",
                                "description": "Usuario para ejecutar el comando"
                            }
                        },
                        "required": ["container_id", "command"]
                    }
                ),
                Tool(
                    name="docker_system_info",
                    description="Obtiene información del sistema Docker",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="docker_system_df",
                    description="Muestra uso de espacio en disco de Docker",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
            
            return ListToolsResult(tools=tools)
        
        @self.server.call_tool()
        async def call_tool(request: CallToolRequest) -> CallToolResult:
            """Ejecuta una herramienta específica"""
            if not self.client:
                return CallToolResult(
                    content=[TextContent(type="text", text="Cliente Docker no disponible")],
                    isError=True
                )
            
            try:
                if request.name == "docker_list_containers":
                    return await self._list_containers(request.arguments)
                elif request.name == "docker_get_container":
                    return await self._get_container(request.arguments)
                elif request.name == "docker_start_container":
                    return await self._start_container(request.arguments)
                elif request.name == "docker_stop_container":
                    return await self._stop_container(request.arguments)
                elif request.name == "docker_restart_container":
                    return await self._restart_container(request.arguments)
                elif request.name == "docker_remove_container":
                    return await self._remove_container(request.arguments)
                elif request.name == "docker_run_container":
                    return await self._run_container(request.arguments)
                elif request.name == "docker_list_images":
                    return await self._list_images(request.arguments)
                elif request.name == "docker_pull_image":
                    return await self._pull_image(request.arguments)
                elif request.name == "docker_remove_image":
                    return await self._remove_image(request.arguments)
                elif request.name == "docker_get_logs":
                    return await self._get_logs(request.arguments)
                elif request.name == "docker_exec_command":
                    return await self._exec_command(request.arguments)
                elif request.name == "docker_system_info":
                    return await self._system_info(request.arguments)
                elif request.name == "docker_system_df":
                    return await self._system_df(request.arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Herramienta desconocida: {request.name}")],
                        isError=True
                    )
            except Exception as e:
                logger.error(f"Error ejecutando herramienta {request.name}: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )
    
    async def _list_containers(self, args: Dict[str, Any]) -> CallToolResult:
        """Lista contenedores Docker"""
        all_containers = args.get("all", False)
        filters = args.get("filters", {})
        
        try:
            containers = self.client.containers.list(all=all_containers, filters=filters)
            result = []
            
            for container in containers:
                result.append({
                    "id": container.short_id,
                    "name": container.name,
                    "image": container.image.tags[0] if container.image.tags else container.image.id,
                    "status": container.status,
                    "created": container.attrs["Created"],
                    "ports": container.ports
                })
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Encontrados {len(result)} contenedores:\n{json.dumps(result, indent=2)}")]
            )
        except DockerException as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error listando contenedores: {str(e)}")],
                isError=True
            )
    
    async def _get_container(self, args: Dict[str, Any]) -> CallToolResult:
        """Obtiene información detallada de un contenedor"""
        container_id = args["container_id"]
        
        try:
            container = self.client.containers.get(container_id)
            
            result = {
                "id": container.id,
                "short_id": container.short_id,
                "name": container.name,
                "image": container.image.tags[0] if container.image.tags else container.image.id,
                "status": container.status,
                "created": container.attrs["Created"],
                "started": container.attrs["State"].get("StartedAt"),
                "ports": container.ports,
                "labels": container.labels,
                "environment": container.attrs["Config"].get("Env", []),
                "mounts": [
                    {
                        "source": mount["Source"],
                        "destination": mount["Destination"],
                        "type": mount["Type"]
                    }
                    for mount in container.attrs.get("Mounts", [])
                ]
            }
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Información del contenedor:\n{json.dumps(result, indent=2)}")]
            )
        except NotFound:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Contenedor {container_id} no encontrado")],
                isError=True
            )
        except DockerException as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error obteniendo contenedor: {str(e)}")],
                isError=True
            )
    
    async def _start_container(self, args: Dict[str, Any]) -> CallToolResult:
        """Inicia un contenedor"""
        container_id = args["container_id"]
        
        try:
            container = self.client.containers.get(container_id)
            container.start()
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Contenedor {container_id} iniciado exitosamente")]
            )
        except NotFound:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Contenedor {container_id} no encontrado")],
                isError=True
            )
        except DockerException as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error iniciando contenedor: {str(e)}")],
                isError=True
            )
    
    async def _stop_container(self, args: Dict[str, Any]) -> CallToolResult:
        """Detiene un contenedor"""
        container_id = args["container_id"]
        timeout = args.get("timeout", 10)
        
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=timeout)
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Contenedor {container_id} detenido exitosamente")]
            )
        except NotFound:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Contenedor {container_id} no encontrado")],
                isError=True
            )
        except DockerException as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error deteniendo contenedor: {str(e)}")],
                isError=True
            )
    
    async def _restart_container(self, args: Dict[str, Any]) -> CallToolResult:
        """Reinicia un contenedor"""
        container_id = args["container_id"]
        timeout = args.get("timeout", 10)
        
        try:
            container = self.client.containers.get(container_id)
            container.restart(timeout=timeout)
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Contenedor {container_id} reiniciado exitosamente")]
            )
        except NotFound:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Contenedor {container_id} no encontrado")],
                isError=True
            )
        except DockerException as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error reiniciando contenedor: {str(e)}")],
                isError=True
            )
    
    async def _remove_container(self, args: Dict[str, Any]) -> CallToolResult:
        """Elimina un contenedor"""
        container_id = args["container_id"]
        force = args.get("force", False)
        v = args.get("v", False)
        
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force, v=v)
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Contenedor {container_id} eliminado exitosamente")]
            )
        except NotFound:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Contenedor {container_id} no encontrado")],
                isError=True
            )
        except DockerException as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error eliminando contenedor: {str(e)}")],
                isError=True
            )
    
    async def _run_container(self, args: Dict[str, Any]) -> CallToolResult:
        """Ejecuta un nuevo contenedor"""
        image = args["image"]
        command = args.get("command")
        name = args.get("name")
        ports = args.get("ports", {})
        environment = args.get("environment", {})
        volumes = args.get("volumes", {})
        detach = args.get("detach", True)
        remove = args.get("remove", False)
        
        try:
            container = self.client.containers.run(
                image=image,
                command=command,
                name=name,
                ports=ports,
                environment=environment,
                volumes=volumes,
                detach=detach,
                remove=remove
            )
            
            if detach:
                result = {
                    "id": container.short_id,
                    "name": container.name,
                    "status": container.status
                }
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Contenedor ejecutado exitosamente:\n{json.dumps(result, indent=2)}")]
                )
            else:
                # Si no es detach, container contiene la salida
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Salida del contenedor:\n{container.decode('utf-8')}")]
                )
                
        except DockerException as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error ejecutando contenedor: {str(e)}")],
                isError=True
            )
    
    async def _list_images(self, args: Dict[str, Any]) -> CallToolResult:
        """Lista imágenes Docker"""
        all_images = args.get("all", False)
        filters = args.get("filters", {})
        
        try:
            images = self.client.images.list(all=all_images, filters=filters)
            result = []
            
            for image in images:
                result.append({
                    "id": image.short_id,
                    "tags": image.tags,
                    "created": image.attrs["Created"],
                    "size": image.attrs["Size"],
                    "labels": image.labels
                })
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Encontradas {len(result)} imágenes:\n{json.dumps(result, indent=2)}")]
            )
        except DockerException as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error listando imágenes: {str(e)}")],
                isError=True
            )
    
    async def _pull_image(self, args: Dict[str, Any]) -> CallToolResult:
        """Descarga una imagen Docker"""
        repository = args["repository"]
        tag = args.get("tag", "latest")
        
        try:
            image = self.client.images.pull(repository, tag=tag)
            
            result = {
                "id": image.short_id,
                "tags": image.tags,
                "size": image.attrs["Size"]
            }
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Imagen descargada exitosamente:\n{json.dumps(result, indent=2)}")]
            )
        except DockerException as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error descargando imagen: {str(e)}")],
                isError=True
            )
    
    async def _remove_image(self, args: Dict[str, Any]) -> CallToolResult:
        """Elimina una imagen Docker"""
        image = args["image"]
        force = args.get("force", False)
        
        try:
            self.client.images.remove(image, force=force)
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Imagen {image} eliminada exitosamente")]
            )
        except NotFound:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Imagen {image} no encontrada")],
                isError=True
            )
        except DockerException as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error eliminando imagen: {str(e)}")],
                isError=True
            )
    
    async def _get_logs(self, args: Dict[str, Any]) -> CallToolResult:
        """Obtiene logs de un contenedor"""
        container_id = args["container_id"]
        tail = args.get("tail", 100)
        follow = args.get("follow", False)
        timestamps = args.get("timestamps", True)
        
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(
                tail=tail,
                follow=follow,
                timestamps=timestamps
            )
            
            if follow:
                # Para logs en tiempo real, solo retornamos las primeras líneas
                log_lines = logs.decode('utf-8').split('\n')[:50]
                log_text = '\n'.join(log_lines)
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Logs del contenedor (primeras 50 líneas):\n{log_text}")]
                )
            else:
                log_text = logs.decode('utf-8')
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Logs del contenedor:\n{log_text}")]
                )
                
        except NotFound:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Contenedor {container_id} no encontrado")],
                isError=True
            )
        except DockerException as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error obteniendo logs: {str(e)}")],
                isError=True
            )
    
    async def _exec_command(self, args: Dict[str, Any]) -> CallToolResult:
        """Ejecuta un comando en un contenedor en ejecución"""
        container_id = args["container_id"]
        command = args["command"]
        workdir = args.get("workdir")
        user = args.get("user")
        
        try:
            container = self.client.containers.get(container_id)
            
            exec_result = container.exec_run(
                command,
                workdir=workdir,
                user=user
            )
            
            result = {
                "exit_code": exec_result.exit_code,
                "output": exec_result.output.decode('utf-8')
            }
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Comando ejecutado:\n{json.dumps(result, indent=2)}")]
            )
        except NotFound:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Contenedor {container_id} no encontrado")],
                isError=True
            )
        except DockerException as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error ejecutando comando: {str(e)}")],
                isError=True
            )
    
    async def _system_info(self, args: Dict[str, Any]) -> CallToolResult:
        """Obtiene información del sistema Docker"""
        try:
            info = self.client.info()
            
            result = {
                "containers": info.get("Containers", 0),
                "containers_running": info.get("ContainersRunning", 0),
                "containers_paused": info.get("ContainersPaused", 0),
                "containers_stopped": info.get("ContainersStopped", 0),
                "images": info.get("Images", 0),
                "server_version": info.get("ServerVersion"),
                "kernel_version": info.get("KernelVersion"),
                "operating_system": info.get("OperatingSystem"),
                "total_memory": info.get("MemTotal"),
                "cpu_count": info.get("NCPU")
            }
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Información del sistema Docker:\n{json.dumps(result, indent=2)}")]
            )
        except DockerException as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error obteniendo información del sistema: {str(e)}")],
                isError=True
            )
    
    async def _system_df(self, args: Dict[str, Any]) -> CallToolResult:
        """Muestra uso de espacio en disco de Docker"""
        try:
            df_info = self.client.df()
            
            result = {
                "images": {
                    "total_count": len(df_info.get("Images", [])),
                    "total_size": sum(img.get("Size", 0) for img in df_info.get("Images", [])),
                    "reclaimable": sum(img.get("Size", 0) for img in df_info.get("Images", []) if not img.get("Containers", 0))
                },
                "containers": {
                    "total_count": len(df_info.get("Containers", [])),
                    "total_size": sum(cont.get("SizeRw", 0) for cont in df_info.get("Containers", [])),
                    "reclaimable": sum(cont.get("SizeRw", 0) for cont in df_info.get("Containers", []) if cont.get("State") != "running")
                },
                "volumes": {
                    "total_count": len(df_info.get("Volumes", [])),
                    "total_size": sum(vol.get("UsageData", {}).get("Size", 0) for vol in df_info.get("Volumes", []) if vol.get("UsageData")),
                    "reclaimable": sum(vol.get("UsageData", {}).get("Size", 0) for vol in df_info.get("Volumes", []) if vol.get("UsageData") and vol.get("UsageData", {}).get("RefCount", 0) == 0)
                }
            }
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Uso de espacio en disco Docker:\n{json.dumps(result, indent=2)}")]
            )
        except DockerException as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error obteniendo información de espacio: {str(e)}")],
                isError=True
            )
    
    async def start(self):
        """Inicia el servidor MCP"""
        logger.info("Iniciando servidor Docker MCP")
    
    async def stop(self):
        """Detiene el servidor MCP"""
        if self.client:
            self.client.close()
        logger.info("Servidor Docker MCP detenido")

# Función para crear y configurar el servidor
def create_docker_server(base_url: Optional[str] = None) -> DockerMCPServer:
    """Crea una instancia del servidor Docker MCP"""
    config = DockerConfig(
        base_url=base_url or "unix://var/run/docker.sock",
        timeout=60,
        version="auto"
    )
    
    return DockerMCPServer(config)

