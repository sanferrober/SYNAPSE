"""
Servidor MCP para GitHub - Integración con Synapse

Este servidor MCP proporciona herramientas para interactuar con GitHub,
incluyendo gestión de repositorios, issues, pull requests y más.
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

import httpx
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
class GitHubConfig:
    """Configuración para el servidor GitHub MCP"""
    token: Optional[str] = None
    base_url: str = "https://api.github.com"
    timeout: int = 30

class GitHubMCPServer:
    """Servidor MCP para integración con GitHub"""
    
    def __init__(self, config: GitHubConfig):
        self.config = config
        self.server = Server("github-mcp-server")
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            headers={
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Synapse-MCP-GitHub/1.0"
            }
        )
        
        if config.token:
            self.client.headers["Authorization"] = f"token {config.token}"
        
        self._register_tools()
    
    def _register_tools(self):
        """Registra todas las herramientas disponibles"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """Lista todas las herramientas disponibles"""
            tools = [
                Tool(
                    name="github_get_repo",
                    description="Obtiene información de un repositorio de GitHub",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "owner": {
                                "type": "string",
                                "description": "Propietario del repositorio"
                            },
                            "repo": {
                                "type": "string", 
                                "description": "Nombre del repositorio"
                            }
                        },
                        "required": ["owner", "repo"]
                    }
                ),
                Tool(
                    name="github_list_repos",
                    description="Lista repositorios de un usuario u organización",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "owner": {
                                "type": "string",
                                "description": "Usuario u organización"
                            },
                            "type": {
                                "type": "string",
                                "enum": ["all", "owner", "member"],
                                "description": "Tipo de repositorios a listar",
                                "default": "all"
                            },
                            "per_page": {
                                "type": "integer",
                                "description": "Número de repositorios por página",
                                "default": 30,
                                "minimum": 1,
                                "maximum": 100
                            }
                        },
                        "required": ["owner"]
                    }
                ),
                Tool(
                    name="github_get_file",
                    description="Obtiene el contenido de un archivo del repositorio",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "owner": {
                                "type": "string",
                                "description": "Propietario del repositorio"
                            },
                            "repo": {
                                "type": "string",
                                "description": "Nombre del repositorio"
                            },
                            "path": {
                                "type": "string",
                                "description": "Ruta del archivo en el repositorio"
                            },
                            "ref": {
                                "type": "string",
                                "description": "Branch, tag o commit SHA",
                                "default": "main"
                            }
                        },
                        "required": ["owner", "repo", "path"]
                    }
                ),
                Tool(
                    name="github_list_issues",
                    description="Lista issues de un repositorio",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "owner": {
                                "type": "string",
                                "description": "Propietario del repositorio"
                            },
                            "repo": {
                                "type": "string",
                                "description": "Nombre del repositorio"
                            },
                            "state": {
                                "type": "string",
                                "enum": ["open", "closed", "all"],
                                "description": "Estado de los issues",
                                "default": "open"
                            },
                            "labels": {
                                "type": "string",
                                "description": "Filtrar por etiquetas (separadas por coma)"
                            },
                            "per_page": {
                                "type": "integer",
                                "description": "Número de issues por página",
                                "default": 30,
                                "minimum": 1,
                                "maximum": 100
                            }
                        },
                        "required": ["owner", "repo"]
                    }
                ),
                Tool(
                    name="github_create_issue",
                    description="Crea un nuevo issue en el repositorio",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "owner": {
                                "type": "string",
                                "description": "Propietario del repositorio"
                            },
                            "repo": {
                                "type": "string",
                                "description": "Nombre del repositorio"
                            },
                            "title": {
                                "type": "string",
                                "description": "Título del issue"
                            },
                            "body": {
                                "type": "string",
                                "description": "Descripción del issue"
                            },
                            "labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Etiquetas para el issue"
                            },
                            "assignees": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Usuarios asignados al issue"
                            }
                        },
                        "required": ["owner", "repo", "title"]
                    }
                ),
                Tool(
                    name="github_list_prs",
                    description="Lista pull requests de un repositorio",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "owner": {
                                "type": "string",
                                "description": "Propietario del repositorio"
                            },
                            "repo": {
                                "type": "string",
                                "description": "Nombre del repositorio"
                            },
                            "state": {
                                "type": "string",
                                "enum": ["open", "closed", "all"],
                                "description": "Estado de los pull requests",
                                "default": "open"
                            },
                            "base": {
                                "type": "string",
                                "description": "Branch base para filtrar PRs"
                            },
                            "head": {
                                "type": "string",
                                "description": "Branch head para filtrar PRs"
                            },
                            "per_page": {
                                "type": "integer",
                                "description": "Número de PRs por página",
                                "default": 30,
                                "minimum": 1,
                                "maximum": 100
                            }
                        },
                        "required": ["owner", "repo"]
                    }
                ),
                Tool(
                    name="github_get_commits",
                    description="Obtiene commits de un repositorio",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "owner": {
                                "type": "string",
                                "description": "Propietario del repositorio"
                            },
                            "repo": {
                                "type": "string",
                                "description": "Nombre del repositorio"
                            },
                            "sha": {
                                "type": "string",
                                "description": "SHA o branch para obtener commits"
                            },
                            "path": {
                                "type": "string",
                                "description": "Filtrar commits que afecten esta ruta"
                            },
                            "since": {
                                "type": "string",
                                "description": "Fecha ISO 8601 para commits desde"
                            },
                            "until": {
                                "type": "string",
                                "description": "Fecha ISO 8601 para commits hasta"
                            },
                            "per_page": {
                                "type": "integer",
                                "description": "Número de commits por página",
                                "default": 30,
                                "minimum": 1,
                                "maximum": 100
                            }
                        },
                        "required": ["owner", "repo"]
                    }
                ),
                Tool(
                    name="github_search_code",
                    description="Busca código en GitHub",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "q": {
                                "type": "string",
                                "description": "Consulta de búsqueda"
                            },
                            "sort": {
                                "type": "string",
                                "enum": ["indexed", "updated"],
                                "description": "Campo para ordenar resultados"
                            },
                            "order": {
                                "type": "string",
                                "enum": ["asc", "desc"],
                                "description": "Orden de los resultados",
                                "default": "desc"
                            },
                            "per_page": {
                                "type": "integer",
                                "description": "Número de resultados por página",
                                "default": 30,
                                "minimum": 1,
                                "maximum": 100
                            }
                        },
                        "required": ["q"]
                    }
                )
            ]
            
            return ListToolsResult(tools=tools)
        
        @self.server.call_tool()
        async def call_tool(request: CallToolRequest) -> CallToolResult:
            """Ejecuta una herramienta específica"""
            try:
                if request.name == "github_get_repo":
                    return await self._get_repo(request.arguments)
                elif request.name == "github_list_repos":
                    return await self._list_repos(request.arguments)
                elif request.name == "github_get_file":
                    return await self._get_file(request.arguments)
                elif request.name == "github_list_issues":
                    return await self._list_issues(request.arguments)
                elif request.name == "github_create_issue":
                    return await self._create_issue(request.arguments)
                elif request.name == "github_list_prs":
                    return await self._list_prs(request.arguments)
                elif request.name == "github_get_commits":
                    return await self._get_commits(request.arguments)
                elif request.name == "github_search_code":
                    return await self._search_code(request.arguments)
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
    
    async def _get_repo(self, args: Dict[str, Any]) -> CallToolResult:
        """Obtiene información de un repositorio"""
        owner = args["owner"]
        repo = args["repo"]
        
        response = await self.client.get(f"/repos/{owner}/{repo}")
        
        if response.status_code == 200:
            repo_data = response.json()
            result = {
                "name": repo_data["name"],
                "full_name": repo_data["full_name"],
                "description": repo_data.get("description"),
                "private": repo_data["private"],
                "html_url": repo_data["html_url"],
                "clone_url": repo_data["clone_url"],
                "ssh_url": repo_data["ssh_url"],
                "default_branch": repo_data["default_branch"],
                "language": repo_data.get("language"),
                "stargazers_count": repo_data["stargazers_count"],
                "forks_count": repo_data["forks_count"],
                "open_issues_count": repo_data["open_issues_count"],
                "created_at": repo_data["created_at"],
                "updated_at": repo_data["updated_at"],
                "pushed_at": repo_data["pushed_at"]
            }
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Repositorio obtenido exitosamente:\n{result}")]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error obteniendo repositorio: {response.status_code} - {response.text}")],
                isError=True
            )
    
    async def _list_repos(self, args: Dict[str, Any]) -> CallToolResult:
        """Lista repositorios de un usuario u organización"""
        owner = args["owner"]
        repo_type = args.get("type", "all")
        per_page = args.get("per_page", 30)
        
        params = {
            "type": repo_type,
            "per_page": per_page,
            "sort": "updated"
        }
        
        response = await self.client.get(f"/users/{owner}/repos", params=params)
        
        if response.status_code == 200:
            repos = response.json()
            result = []
            
            for repo in repos:
                result.append({
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo.get("description"),
                    "private": repo["private"],
                    "html_url": repo["html_url"],
                    "language": repo.get("language"),
                    "stargazers_count": repo["stargazers_count"],
                    "updated_at": repo["updated_at"]
                })
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Encontrados {len(result)} repositorios:\n{result}")]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error listando repositorios: {response.status_code} - {response.text}")],
                isError=True
            )
    
    async def _get_file(self, args: Dict[str, Any]) -> CallToolResult:
        """Obtiene el contenido de un archivo"""
        owner = args["owner"]
        repo = args["repo"]
        path = args["path"]
        ref = args.get("ref", "main")
        
        params = {"ref": ref}
        response = await self.client.get(f"/repos/{owner}/{repo}/contents/{path}", params=params)
        
        if response.status_code == 200:
            file_data = response.json()
            
            if file_data["type"] == "file":
                import base64
                content = base64.b64decode(file_data["content"]).decode('utf-8')
                
                result = {
                    "name": file_data["name"],
                    "path": file_data["path"],
                    "size": file_data["size"],
                    "sha": file_data["sha"],
                    "content": content,
                    "download_url": file_data.get("download_url")
                }
                
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Archivo obtenido exitosamente:\n{result}")]
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"La ruta especificada no es un archivo: {file_data['type']}")],
                    isError=True
                )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error obteniendo archivo: {response.status_code} - {response.text}")],
                isError=True
            )
    
    async def _list_issues(self, args: Dict[str, Any]) -> CallToolResult:
        """Lista issues de un repositorio"""
        owner = args["owner"]
        repo = args["repo"]
        state = args.get("state", "open")
        labels = args.get("labels")
        per_page = args.get("per_page", 30)
        
        params = {
            "state": state,
            "per_page": per_page,
            "sort": "updated"
        }
        
        if labels:
            params["labels"] = labels
        
        response = await self.client.get(f"/repos/{owner}/{repo}/issues", params=params)
        
        if response.status_code == 200:
            issues = response.json()
            result = []
            
            for issue in issues:
                # Filtrar pull requests (GitHub API incluye PRs en issues)
                if "pull_request" not in issue:
                    result.append({
                        "number": issue["number"],
                        "title": issue["title"],
                        "body": issue.get("body", "")[:200] + "..." if issue.get("body") and len(issue.get("body", "")) > 200 else issue.get("body", ""),
                        "state": issue["state"],
                        "user": issue["user"]["login"],
                        "labels": [label["name"] for label in issue["labels"]],
                        "assignees": [assignee["login"] for assignee in issue["assignees"]],
                        "created_at": issue["created_at"],
                        "updated_at": issue["updated_at"],
                        "html_url": issue["html_url"]
                    })
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Encontrados {len(result)} issues:\n{result}")]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error listando issues: {response.status_code} - {response.text}")],
                isError=True
            )
    
    async def _create_issue(self, args: Dict[str, Any]) -> CallToolResult:
        """Crea un nuevo issue"""
        if not self.config.token:
            return CallToolResult(
                content=[TextContent(type="text", text="Token de GitHub requerido para crear issues")],
                isError=True
            )
        
        owner = args["owner"]
        repo = args["repo"]
        title = args["title"]
        body = args.get("body", "")
        labels = args.get("labels", [])
        assignees = args.get("assignees", [])
        
        data = {
            "title": title,
            "body": body,
            "labels": labels,
            "assignees": assignees
        }
        
        response = await self.client.post(f"/repos/{owner}/{repo}/issues", json=data)
        
        if response.status_code == 201:
            issue = response.json()
            result = {
                "number": issue["number"],
                "title": issue["title"],
                "state": issue["state"],
                "html_url": issue["html_url"],
                "created_at": issue["created_at"]
            }
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Issue creado exitosamente:\n{result}")]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error creando issue: {response.status_code} - {response.text}")],
                isError=True
            )
    
    async def _list_prs(self, args: Dict[str, Any]) -> CallToolResult:
        """Lista pull requests de un repositorio"""
        owner = args["owner"]
        repo = args["repo"]
        state = args.get("state", "open")
        base = args.get("base")
        head = args.get("head")
        per_page = args.get("per_page", 30)
        
        params = {
            "state": state,
            "per_page": per_page,
            "sort": "updated"
        }
        
        if base:
            params["base"] = base
        if head:
            params["head"] = head
        
        response = await self.client.get(f"/repos/{owner}/{repo}/pulls", params=params)
        
        if response.status_code == 200:
            prs = response.json()
            result = []
            
            for pr in prs:
                result.append({
                    "number": pr["number"],
                    "title": pr["title"],
                    "body": pr.get("body", "")[:200] + "..." if pr.get("body") and len(pr.get("body", "")) > 200 else pr.get("body", ""),
                    "state": pr["state"],
                    "user": pr["user"]["login"],
                    "base": pr["base"]["ref"],
                    "head": pr["head"]["ref"],
                    "mergeable": pr.get("mergeable"),
                    "created_at": pr["created_at"],
                    "updated_at": pr["updated_at"],
                    "html_url": pr["html_url"]
                })
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Encontrados {len(result)} pull requests:\n{result}")]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error listando pull requests: {response.status_code} - {response.text}")],
                isError=True
            )
    
    async def _get_commits(self, args: Dict[str, Any]) -> CallToolResult:
        """Obtiene commits de un repositorio"""
        owner = args["owner"]
        repo = args["repo"]
        sha = args.get("sha")
        path = args.get("path")
        since = args.get("since")
        until = args.get("until")
        per_page = args.get("per_page", 30)
        
        params = {"per_page": per_page}
        
        if sha:
            params["sha"] = sha
        if path:
            params["path"] = path
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        
        response = await self.client.get(f"/repos/{owner}/{repo}/commits", params=params)
        
        if response.status_code == 200:
            commits = response.json()
            result = []
            
            for commit in commits:
                result.append({
                    "sha": commit["sha"],
                    "message": commit["commit"]["message"],
                    "author": commit["commit"]["author"]["name"],
                    "author_email": commit["commit"]["author"]["email"],
                    "date": commit["commit"]["author"]["date"],
                    "html_url": commit["html_url"]
                })
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Encontrados {len(result)} commits:\n{result}")]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error obteniendo commits: {response.status_code} - {response.text}")],
                isError=True
            )
    
    async def _search_code(self, args: Dict[str, Any]) -> CallToolResult:
        """Busca código en GitHub"""
        query = args["q"]
        sort = args.get("sort")
        order = args.get("order", "desc")
        per_page = args.get("per_page", 30)
        
        params = {
            "q": query,
            "per_page": per_page,
            "order": order
        }
        
        if sort:
            params["sort"] = sort
        
        response = await self.client.get("/search/code", params=params)
        
        if response.status_code == 200:
            search_result = response.json()
            items = search_result.get("items", [])
            result = []
            
            for item in items:
                result.append({
                    "name": item["name"],
                    "path": item["path"],
                    "repository": item["repository"]["full_name"],
                    "html_url": item["html_url"],
                    "score": item["score"]
                })
            
            return CallToolResult(
                content=[TextContent(type="text", text=f"Encontrados {len(result)} resultados de código:\n{result}")]
            )
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error buscando código: {response.status_code} - {response.text}")],
                isError=True
            )
    
    async def start(self):
        """Inicia el servidor MCP"""
        logger.info("Iniciando servidor GitHub MCP")
        # El servidor se inicia automáticamente cuando se registra
    
    async def stop(self):
        """Detiene el servidor MCP"""
        await self.client.aclose()
        logger.info("Servidor GitHub MCP detenido")

# Función para crear y configurar el servidor
def create_github_server(token: Optional[str] = None) -> GitHubMCPServer:
    """Crea una instancia del servidor GitHub MCP"""
    config = GitHubConfig(
        token=token or os.getenv("GITHUB_TOKEN"),
        base_url=os.getenv("GITHUB_API_URL", "https://api.github.com"),
        timeout=int(os.getenv("GITHUB_TIMEOUT", "30"))
    )
    
    return GitHubMCPServer(config)

