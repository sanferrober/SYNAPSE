"""
Servidor MCP para VS Code - Integración con Synapse

Este servidor MCP proporciona herramientas para interactuar con Visual Studio Code,
incluyendo gestión de archivos, proyectos, extensiones y debugging.
"""

import os
import json
import asyncio
import logging
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

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
class VSCodeConfig:
    """Configuración para el servidor VS Code MCP"""
    code_command: str = "code"
    workspace_dir: Optional[str] = None
    timeout: int = 30

class VSCodeMCPServer:
    """Servidor MCP para integración con VS Code"""
    
    def __init__(self, config: VSCodeConfig):
        self.config = config
        self.server = Server("vscode-mcp-server")
        self.workspace_dir = config.workspace_dir or os.getcwd()
        
        self._register_tools()
    
    def _register_tools(self):
        """Registra todas las herramientas disponibles"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """Lista todas las herramientas disponibles"""
            tools = [
                Tool(
                    name="vscode_open_file",
                    description="Abre un archivo en VS Code",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Ruta del archivo a abrir"
                            },
                            "line": {
                                "type": "integer",
                                "description": "Número de línea para posicionar el cursor"
                            },
                            "column": {
                                "type": "integer",
                                "description": "Número de columna para posicionar el cursor"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="vscode_open_folder",
                    description="Abre una carpeta como workspace en VS Code",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "folder_path": {
                                "type": "string",
                                "description": "Ruta de la carpeta a abrir"
                            },
                            "new_window": {
                                "type": "boolean",
                                "description": "Abrir en nueva ventana",
                                "default": False
                            }
                        },
                        "required": ["folder_path"]
                    }
                ),
                Tool(
                    name="vscode_create_file",
                    description="Crea un nuevo archivo en el workspace",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Ruta del archivo a crear"
                            },
                            "content": {
                                "type": "string",
                                "description": "Contenido inicial del archivo",
                                "default": ""
                            },
                            "open_after_create": {
                                "type": "boolean",
                                "description": "Abrir el archivo después de crearlo",
                                "default": True
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="vscode_create_folder",
                    description="Crea una nueva carpeta en el workspace",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "folder_path": {
                                "type": "string",
                                "description": "Ruta de la carpeta a crear"
                            }
                        },
                        "required": ["folder_path"]
                    }
                ),
                Tool(
                    name="vscode_list_extensions",
                    description="Lista las extensiones instaladas en VS Code",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "show_versions": {
                                "type": "boolean",
                                "description": "Mostrar versiones de las extensiones",
                                "default": True
                            }
                        }
                    }
                ),
                Tool(
                    name="vscode_install_extension",
                    description="Instala una extensión en VS Code",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "extension_id": {
                                "type": "string",
                                "description": "ID de la extensión a instalar (ej: ms-python.python)"
                            },
                            "force": {
                                "type": "boolean",
                                "description": "Forzar reinstalación si ya está instalada",
                                "default": False
                            }
                        },
                        "required": ["extension_id"]
                    }
                ),
                Tool(
                    name="vscode_uninstall_extension",
                    description="Desinstala una extensión de VS Code",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "extension_id": {
                                "type": "string",
                                "description": "ID de la extensión a desinstalar"
                            }
                        },
                        "required": ["extension_id"]
                    }
                ),
                Tool(
                    name="vscode_search_extensions",
                    description="Busca extensiones en el marketplace de VS Code",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Término de búsqueda"
                            },
                            "category": {
                                "type": "string",
                                "description": "Categoría de extensiones",
                                "enum": ["Programming Languages", "Snippets", "Linters", "Themes", "Debuggers", "Formatters", "Keymaps", "SCM Providers", "Other"]
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Número máximo de resultados",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 50
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="vscode_get_workspace_info",
                    description="Obtiene información del workspace actual",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="vscode_list_workspace_files",
                    description="Lista archivos en el workspace",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pattern": {
                                "type": "string",
                                "description": "Patrón de archivos a buscar (ej: *.py, **/*.js)",
                                "default": "**/*"
                            },
                            "exclude_patterns": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Patrones de archivos a excluir",
                                "default": ["node_modules/**", ".git/**", "**/__pycache__/**"]
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Número máximo de resultados",
                                "default": 100,
                                "minimum": 1,
                                "maximum": 1000
                            }
                        }
                    }
                ),
                Tool(
                    name="vscode_run_task",
                    description="Ejecuta una tarea definida en tasks.json",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_name": {
                                "type": "string",
                                "description": "Nombre de la tarea a ejecutar"
                            }
                        },
                        "required": ["task_name"]
                    }
                ),
                Tool(
                    name="vscode_create_task",
                    description="Crea una nueva tarea en tasks.json",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_name": {
                                "type": "string",
                                "description": "Nombre de la tarea"
                            },
                            "command": {
                                "type": "string",
                                "description": "Comando a ejecutar"
                            },
                            "args": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Argumentos del comando",
                                "default": []
                            },
                            "group": {
                                "type": "string",
                                "description": "Grupo de la tarea",
                                "enum": ["build", "test", "clean"],
                                "default": "build"
                            },
                            "presentation": {
                                "type": "object",
                                "description": "Configuración de presentación de la tarea"
                            }
                        },
                        "required": ["task_name", "command"]
                    }
                ),
                Tool(
                    name="vscode_create_launch_config",
                    description="Crea una configuración de debug en launch.json",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Nombre de la configuración"
                            },
                            "type": {
                                "type": "string",
                                "description": "Tipo de debugger",
                                "enum": ["python", "node", "chrome", "firefox", "go", "java", "csharp"]
                            },
                            "request": {
                                "type": "string",
                                "description": "Tipo de request",
                                "enum": ["launch", "attach"],
                                "default": "launch"
                            },
                            "program": {
                                "type": "string",
                                "description": "Programa a ejecutar"
                            },
                            "args": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Argumentos del programa",
                                "default": []
                            },
                            "cwd": {
                                "type": "string",
                                "description": "Directorio de trabajo"
                            },
                            "env": {
                                "type": "object",
                                "description": "Variables de entorno"
                            }
                        },
                        "required": ["name", "type"]
                    }
                ),
                Tool(
                    name="vscode_format_document",
                    description="Formatea un documento usando VS Code",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Ruta del archivo a formatear"
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="vscode_get_settings",
                    description="Obtiene configuraciones de VS Code",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "scope": {
                                "type": "string",
                                "description": "Ámbito de las configuraciones",
                                "enum": ["user", "workspace"],
                                "default": "workspace"
                            }
                        }
                    }
                ),
                Tool(
                    name="vscode_update_settings",
                    description="Actualiza configuraciones de VS Code",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "settings": {
                                "type": "object",
                                "description": "Configuraciones a actualizar"
                            },
                            "scope": {
                                "type": "string",
                                "description": "Ámbito de las configuraciones",
                                "enum": ["user", "workspace"],
                                "default": "workspace"
                            }
                        },
                        "required": ["settings"]
                    }
                )
            ]
            
            return ListToolsResult(tools=tools)
        
        @self.server.call_tool()
        async def call_tool(request: CallToolRequest) -> CallToolResult:
            """Ejecuta una herramienta específica"""
            try:
                if request.name == "vscode_open_file":
                    return await self._open_file(request.arguments)
                elif request.name == "vscode_open_folder":
                    return await self._open_folder(request.arguments)
                elif request.name == "vscode_create_file":
                    return await self._create_file(request.arguments)
                elif request.name == "vscode_create_folder":
                    return await self._create_folder(request.arguments)
                elif request.name == "vscode_list_extensions":
                    return await self._list_extensions(request.arguments)
                elif request.name == "vscode_install_extension":
                    return await self._install_extension(request.arguments)
                elif request.name == "vscode_uninstall_extension":
                    return await self._uninstall_extension(request.arguments)
                elif request.name == "vscode_search_extensions":
                    return await self._search_extensions(request.arguments)
                elif request.name == "vscode_get_workspace_info":
                    return await self._get_workspace_info(request.arguments)
                elif request.name == "vscode_list_workspace_files":
                    return await self._list_workspace_files(request.arguments)
                elif request.name == "vscode_run_task":
                    return await self._run_task(request.arguments)
                elif request.name == "vscode_create_task":
                    return await self._create_task(request.arguments)
                elif request.name == "vscode_create_launch_config":
                    return await self._create_launch_config(request.arguments)
                elif request.name == "vscode_format_document":
                    return await self._format_document(request.arguments)
                elif request.name == "vscode_get_settings":
                    return await self._get_settings(request.arguments)
                elif request.name == "vscode_update_settings":
                    return await self._update_settings(request.arguments)
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
    
    async def _run_command(self, command: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
        """Ejecuta un comando y retorna el resultado"""
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=cwd or self.workspace_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.config.timeout
            )
            
            return {
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8'),
                "stderr": stderr.decode('utf-8')
            }
        except asyncio.TimeoutError:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": "Comando excedió el tiempo límite"
            }
        except Exception as e:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e)
            }
    
    async def _open_file(self, args: Dict[str, Any]) -> CallToolResult:
        """Abre un archivo en VS Code"""
        file_path = args["file_path"]
        line = args.get("line")
        column = args.get("column")
        
        # Construir comando
        command = [self.config.code_command]
        
        if line and column:
            command.extend(["-g", f"{file_path}:{line}:{column}"])
        elif line:
            command.extend(["-g", f"{file_path}:{line}"])
        else:
            command.append(file_path)
        
        result = await self._run_command(command)
        
        if result["returncode"] == 0:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Archivo {file_path} abierto exitosamente en VS Code")]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error abriendo archivo: {result['stderr']}")],
                isError=True
            )
    
    async def _open_folder(self, args: Dict[str, Any]) -> CallToolResult:
        """Abre una carpeta como workspace en VS Code"""
        folder_path = args["folder_path"]
        new_window = args.get("new_window", False)
        
        command = [self.config.code_command]
        
        if new_window:
            command.append("-n")
        
        command.append(folder_path)
        
        result = await self._run_command(command)
        
        if result["returncode"] == 0:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Carpeta {folder_path} abierta exitosamente en VS Code")]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error abriendo carpeta: {result['stderr']}")],
                isError=True
            )
    
    async def _create_file(self, args: Dict[str, Any]) -> CallToolResult:
        """Crea un nuevo archivo en el workspace"""
        file_path = args["file_path"]
        content = args.get("content", "")
        open_after_create = args.get("open_after_create", True)
        
        try:
            # Crear directorios padre si no existen
            full_path = Path(self.workspace_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Escribir contenido al archivo
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Abrir en VS Code si se solicita
            if open_after_create:
                await self._open_file({"file_path": str(full_path)})
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Archivo {file_path} creado exitosamente")]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error creando archivo: {str(e)}")],
                isError=True
            )
    
    async def _create_folder(self, args: Dict[str, Any]) -> CallToolResult:
        """Crea una nueva carpeta en el workspace"""
        folder_path = args["folder_path"]
        
        try:
            full_path = Path(self.workspace_dir) / folder_path
            full_path.mkdir(parents=True, exist_ok=True)
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Carpeta {folder_path} creada exitosamente")]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error creando carpeta: {str(e)}")],
                isError=True
            )
    
    async def _list_extensions(self, args: Dict[str, Any]) -> CallToolResult:
        """Lista las extensiones instaladas en VS Code"""
        show_versions = args.get("show_versions", True)
        
        command = [self.config.code_command, "--list-extensions"]
        if show_versions:
            command.append("--show-versions")
        
        result = await self._run_command(command)
        
        if result["returncode"] == 0:
            extensions = result["stdout"].strip().split('\n') if result["stdout"].strip() else []
            return CallToolResult(
                content=[TextContent(type="text", text=f"Extensiones instaladas ({len(extensions)}):\n" + "\n".join(extensions))]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error listando extensiones: {result['stderr']}")],
                isError=True
            )
    
    async def _install_extension(self, args: Dict[str, Any]) -> CallToolResult:
        """Instala una extensión en VS Code"""
        extension_id = args["extension_id"]
        force = args.get("force", False)
        
        command = [self.config.code_command, "--install-extension", extension_id]
        if force:
            command.append("--force")
        
        result = await self._run_command(command)
        
        if result["returncode"] == 0:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Extensión {extension_id} instalada exitosamente")]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error instalando extensión: {result['stderr']}")],
                isError=True
            )
    
    async def _uninstall_extension(self, args: Dict[str, Any]) -> CallToolResult:
        """Desinstala una extensión de VS Code"""
        extension_id = args["extension_id"]
        
        command = [self.config.code_command, "--uninstall-extension", extension_id]
        
        result = await self._run_command(command)
        
        if result["returncode"] == 0:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Extensión {extension_id} desinstalada exitosamente")]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error desinstalando extensión: {result['stderr']}")],
                isError=True
            )
    
    async def _search_extensions(self, args: Dict[str, Any]) -> CallToolResult:
        """Busca extensiones en el marketplace de VS Code"""
        # Esta funcionalidad requiere acceso a la API del marketplace
        # Por simplicidad, retornamos un mensaje informativo
        query = args["query"]
        
        return CallToolResult(
            content=[TextContent(type="text", text=f"Búsqueda de extensiones para '{query}' - Esta funcionalidad requiere acceso directo al marketplace de VS Code")]
        )
    
    async def _get_workspace_info(self, args: Dict[str, Any]) -> CallToolResult:
        """Obtiene información del workspace actual"""
        try:
            workspace_path = Path(self.workspace_dir)
            
            info = {
                "workspace_path": str(workspace_path.absolute()),
                "workspace_name": workspace_path.name,
                "exists": workspace_path.exists(),
                "is_directory": workspace_path.is_dir() if workspace_path.exists() else False
            }
            
            # Buscar archivos de configuración de VS Code
            vscode_dir = workspace_path / ".vscode"
            if vscode_dir.exists():
                info["vscode_config"] = {
                    "settings_json": (vscode_dir / "settings.json").exists(),
                    "tasks_json": (vscode_dir / "tasks.json").exists(),
                    "launch_json": (vscode_dir / "launch.json").exists(),
                    "extensions_json": (vscode_dir / "extensions.json").exists()
                }
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Información del workspace:\n{json.dumps(info, indent=2)}")]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error obteniendo información del workspace: {str(e)}")],
                isError=True
            )
    
    async def _list_workspace_files(self, args: Dict[str, Any]) -> CallToolResult:
        """Lista archivos en el workspace"""
        pattern = args.get("pattern", "**/*")
        exclude_patterns = args.get("exclude_patterns", ["node_modules/**", ".git/**", "**/__pycache__/**"])
        max_results = args.get("max_results", 100)
        
        try:
            workspace_path = Path(self.workspace_dir)
            files = []
            
            # Usar glob para buscar archivos
            for file_path in workspace_path.glob(pattern):
                if file_path.is_file():
                    relative_path = file_path.relative_to(workspace_path)
                    
                    # Verificar patrones de exclusión
                    excluded = False
                    for exclude_pattern in exclude_patterns:
                        if relative_path.match(exclude_pattern):
                            excluded = True
                            break
                    
                    if not excluded:
                        files.append({
                            "path": str(relative_path),
                            "size": file_path.stat().st_size,
                            "modified": file_path.stat().st_mtime
                        })
                        
                        if len(files) >= max_results:
                            break
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Archivos encontrados ({len(files)}):\n{json.dumps(files, indent=2)}")]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error listando archivos: {str(e)}")],
                isError=True
            )
    
    async def _run_task(self, args: Dict[str, Any]) -> CallToolResult:
        """Ejecuta una tarea definida en tasks.json"""
        task_name = args["task_name"]
        
        # Buscar tasks.json
        tasks_file = Path(self.workspace_dir) / ".vscode" / "tasks.json"
        
        if not tasks_file.exists():
            return CallToolResult(
                content=[TextContent(type="text", text="No se encontró archivo tasks.json en el workspace")],
                isError=True
            )
        
        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks_config = json.load(f)
            
            # Buscar la tarea
            task = None
            for t in tasks_config.get("tasks", []):
                if t.get("label") == task_name:
                    task = t
                    break
            
            if not task:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Tarea '{task_name}' no encontrada")],
                    isError=True
                )
            
            # Ejecutar la tarea usando VS Code
            command = [self.config.code_command, "--task", task_name]
            result = await self._run_command(command)
            
            if result["returncode"] == 0:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Tarea '{task_name}' ejecutada exitosamente")]
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error ejecutando tarea: {result['stderr']}")],
                    isError=True
                )
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error ejecutando tarea: {str(e)}")],
                isError=True
            )
    
    async def _create_task(self, args: Dict[str, Any]) -> CallToolResult:
        """Crea una nueva tarea en tasks.json"""
        task_name = args["task_name"]
        command = args["command"]
        task_args = args.get("args", [])
        group = args.get("group", "build")
        presentation = args.get("presentation", {})
        
        try:
            # Crear directorio .vscode si no existe
            vscode_dir = Path(self.workspace_dir) / ".vscode"
            vscode_dir.mkdir(exist_ok=True)
            
            tasks_file = vscode_dir / "tasks.json"
            
            # Cargar tasks.json existente o crear nuevo
            if tasks_file.exists():
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    tasks_config = json.load(f)
            else:
                tasks_config = {
                    "version": "2.0.0",
                    "tasks": []
                }
            
            # Crear nueva tarea
            new_task = {
                "label": task_name,
                "type": "shell",
                "command": command,
                "args": task_args,
                "group": group,
                "presentation": presentation
            }
            
            # Añadir o reemplazar tarea
            existing_task_index = None
            for i, task in enumerate(tasks_config["tasks"]):
                if task.get("label") == task_name:
                    existing_task_index = i
                    break
            
            if existing_task_index is not None:
                tasks_config["tasks"][existing_task_index] = new_task
            else:
                tasks_config["tasks"].append(new_task)
            
            # Guardar tasks.json
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_config, f, indent=2)
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Tarea '{task_name}' creada exitosamente")]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error creando tarea: {str(e)}")],
                isError=True
            )
    
    async def _create_launch_config(self, args: Dict[str, Any]) -> CallToolResult:
        """Crea una configuración de debug en launch.json"""
        name = args["name"]
        config_type = args["type"]
        request = args.get("request", "launch")
        program = args.get("program")
        launch_args = args.get("args", [])
        cwd = args.get("cwd")
        env = args.get("env", {})
        
        try:
            # Crear directorio .vscode si no existe
            vscode_dir = Path(self.workspace_dir) / ".vscode"
            vscode_dir.mkdir(exist_ok=True)
            
            launch_file = vscode_dir / "launch.json"
            
            # Cargar launch.json existente o crear nuevo
            if launch_file.exists():
                with open(launch_file, 'r', encoding='utf-8') as f:
                    launch_config = json.load(f)
            else:
                launch_config = {
                    "version": "0.2.0",
                    "configurations": []
                }
            
            # Crear nueva configuración
            new_config = {
                "name": name,
                "type": config_type,
                "request": request
            }
            
            if program:
                new_config["program"] = program
            if launch_args:
                new_config["args"] = launch_args
            if cwd:
                new_config["cwd"] = cwd
            if env:
                new_config["env"] = env
            
            # Añadir configuraciones específicas por tipo
            if config_type == "python":
                new_config["console"] = "integratedTerminal"
            elif config_type == "node":
                new_config["skipFiles"] = ["<node_internals>/**"]
            
            # Añadir o reemplazar configuración
            existing_config_index = None
            for i, config in enumerate(launch_config["configurations"]):
                if config.get("name") == name:
                    existing_config_index = i
                    break
            
            if existing_config_index is not None:
                launch_config["configurations"][existing_config_index] = new_config
            else:
                launch_config["configurations"].append(new_config)
            
            # Guardar launch.json
            with open(launch_file, 'w', encoding='utf-8') as f:
                json.dump(launch_config, f, indent=2)
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Configuración de debug '{name}' creada exitosamente")]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error creando configuración de debug: {str(e)}")],
                isError=True
            )
    
    async def _format_document(self, args: Dict[str, Any]) -> CallToolResult:
        """Formatea un documento usando VS Code"""
        file_path = args["file_path"]
        
        # Usar comando de VS Code para formatear
        command = [self.config.code_command, "--wait", "--command", "editor.action.formatDocument", file_path]
        
        result = await self._run_command(command)
        
        if result["returncode"] == 0:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Documento {file_path} formateado exitosamente")]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error formateando documento: {result['stderr']}")],
                isError=True
            )
    
    async def _get_settings(self, args: Dict[str, Any]) -> CallToolResult:
        """Obtiene configuraciones de VS Code"""
        scope = args.get("scope", "workspace")
        
        try:
            if scope == "workspace":
                settings_file = Path(self.workspace_dir) / ".vscode" / "settings.json"
            else:
                # Para configuraciones de usuario, la ubicación varía por OS
                return CallToolResult(
                    content=[TextContent(type="text", text="Obtención de configuraciones de usuario no implementada")],
                    isError=True
                )
            
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Configuraciones del workspace:\n{json.dumps(settings, indent=2)}")]
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text="No se encontró archivo de configuraciones en el workspace")]
                )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error obteniendo configuraciones: {str(e)}")],
                isError=True
            )
    
    async def _update_settings(self, args: Dict[str, Any]) -> CallToolResult:
        """Actualiza configuraciones de VS Code"""
        settings = args["settings"]
        scope = args.get("scope", "workspace")
        
        try:
            if scope == "workspace":
                # Crear directorio .vscode si no existe
                vscode_dir = Path(self.workspace_dir) / ".vscode"
                vscode_dir.mkdir(exist_ok=True)
                
                settings_file = vscode_dir / "settings.json"
                
                # Cargar configuraciones existentes o crear nuevas
                if settings_file.exists():
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        current_settings = json.load(f)
                else:
                    current_settings = {}
                
                # Actualizar configuraciones
                current_settings.update(settings)
                
                # Guardar configuraciones
                with open(settings_file, 'w', encoding='utf-8') as f:
                    json.dump(current_settings, f, indent=2)
                
                return CallToolResult(
                    content=[TextContent(type="text", text="Configuraciones del workspace actualizadas exitosamente")]
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text="Actualización de configuraciones de usuario no implementada")],
                    isError=True
                )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error actualizando configuraciones: {str(e)}")],
                isError=True
            )
    
    async def start(self):
        """Inicia el servidor MCP"""
        logger.info("Iniciando servidor VS Code MCP")
    
    async def stop(self):
        """Detiene el servidor MCP"""
        logger.info("Servidor VS Code MCP detenido")

# Función para crear y configurar el servidor
def create_vscode_server(workspace_dir: Optional[str] = None, code_command: str = "code") -> VSCodeMCPServer:
    """Crea una instancia del servidor VS Code MCP"""
    config = VSCodeConfig(
        code_command=code_command,
        workspace_dir=workspace_dir,
        timeout=30
    )
    
    return VSCodeMCPServer(config)

