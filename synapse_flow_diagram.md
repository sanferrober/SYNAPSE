# Diagrama de Flujo de Synapse

## Arquitectura General

```mermaid
graph TD
    A[Usuario] -->|Envía mensaje| B[Frontend - App.js]
    B -->|WebSocket| C[Backend - synapse_server_final.py]
    C -->|Análisis de Intención| D[Análisis de Intención]
    D -->|Genera Plan| E[Generación de Plan]
    E -->|Ejecuta Plan| F[Ejecución de Plan]
    F -->|Ejecuta Herramientas| G[Herramientas]
    G -->|Core Tools| H[Herramientas Core]
    G -->|MCP Tools| I[Herramientas MCP]
    F -->|Genera Outputs| J[Generación de Outputs]
    J -->|WebSocket| B
    C -->|Almacena en Memoria| K[Sistema de Memoria]
    C -->|Configuración LLM| L[Configuración LLM]
```

## Flujo Detallado

### 1. Entrada del Usuario y Procesamiento Inicial

```mermaid
sequenceDiagram
    Usuario->>Frontend: Envía mensaje
    Frontend->>Backend: Emite evento 'user_message'
    Backend->>Backend: process_message()
    Backend->>Backend: analyze_intent()
    Backend->>Frontend: Emite evento 'message_response'
```

**Archivos Relevantes:**
- Frontend: [synapse-ui-new/src/App.js](synapse-ui-new/src/App.js)
- Backend: [synapse_server_final.py](synapse_server_final.py)
- Análisis de Intención: Función `analyze_intent()` en [synapse_server_final.py](synapse_server_final.py)

### 2. Generación y Ejecución del Plan

```mermaid
sequenceDiagram
    Backend->>Backend: generate_plan()
    Backend->>Frontend: Emite evento 'plan_generated'
    Backend->>Backend: execute_plan_automatically()
    loop Para cada paso del plan
        Backend->>Backend: execute_step()
        Backend->>Frontend: Emite evento 'plan_step_update'
    end
    Backend->>Frontend: Emite evento 'plan_completed'
```

**Archivos Relevantes:**
- Generación de Plan: Función `generate_plan()` en [synapse_server_final.py](synapse_server_final.py)
- Ejecución de Plan: Función `execute_plan_automatically()` en [synapse_server_final.py](synapse_server_final.py)
- Ejecución de Pasos: Función `execute_step()` en [synapse_server_final.py](synapse_server_final.py)

### 3. Ejecución de Herramientas

```mermaid
graph TD
    A[execute_step] -->|Determina herramienta| B{Tipo de Herramienta}
    B -->|Core Tool| C[execute_core_tool]
    B -->|MCP Tool| D[execute_mcp_tool]
    C -->|web_search| E[Web Search]
    C -->|data_analyzer| F[Data Analyzer]
    C -->|code_generator| G[Code Generator]
    C -->|task_planner| H[Task Planner]
    D -->|web_search_mcp| I[Web Search MCP]
    D -->|github_mcp| J[GitHub MCP]
    D -->|brave_search_mcp| K[Brave Search MCP]
    D -->|Otras herramientas MCP| L[Otras MCP]
```

**Archivos Relevantes:**
- Ejecución de Herramientas Core: Función `execute_core_tool()` en [synapse_server_final.py](synapse_server_final.py)
- Ejecución de Herramientas MCP: Función `execute_mcp_tool()` en [synapse_server_final.py](synapse_server_final.py)
- Implementación de Herramientas MCP Reales: [mcp_integration/real_mcp_tools.py](mcp_integration/real_mcp_tools.py)

### 4. Análisis Dinámico y Expansión del Plan

```mermaid
sequenceDiagram
    Backend->>Backend: analyze_step_results()
    alt Necesita expansión
        Backend->>Backend: should_expand_plan()
        Backend->>Backend: generate_dynamic_steps()
        Backend->>Backend: notify_plan_expansion()
        Backend->>Frontend: Emite evento 'plan_expansion_notification'
    end
```

**Archivos Relevantes:**
- Análisis Dinámico: [dynamic_analysis.py](dynamic_analysis.py)
- Generación de Outputs: [output_generators.py](output_generators.py)

### 5. Sistema de Memoria

```mermaid
graph TD
    A[Backend] -->|Guarda conversación| B[memory_store]
    A -->|Actualiza preferencias| B
    A -->|Aprende patrones| B
    A -->|Guarda outputs| B
    B -->|Persistencia| C[synapse_memory.json]
    A -->|Crea backup| D[Directorio backups]
```

**Archivos Relevantes:**
- Sistema de Memoria: Funciones de memoria en [synapse_server_final.py](synapse_server_final.py)
- Análisis de Memoria: [ANALISIS_MEMORIA_SYNAPSE.md](ANALISIS_MEMORIA_SYNAPSE.md)
- Memoria Mejorada: [MEMORIA_MEJORADA_SYNAPSE.md](MEMORIA_MEJORADA_SYNAPSE.md)

### 6. Configuración de LLMs

```mermaid
graph TD
    A[llm_config.json] -->|Carga configuración| B[load_llm_config_from_disk]
    C[Frontend - LLMSelector] -->|Actualiza configuración| D[update_llm_config]
    D -->|Guarda configuración| A
```

**Archivos Relevantes:**
- Configuración LLM: [llm_config.json](llm_config.json)
- Selector de LLM: [synapse-ui-new/src/components/LLMSelector.js](synapse-ui-new/src/components/LLMSelector.js)
- Documentación: [CONFIGURACION_LLMS_SYNAPSE.md](CONFIGURACION_LLMS_SYNAPSE.md)

## Flujo de Datos Completo

```mermaid
flowchart TD
    A[Usuario] -->|Mensaje| B[Frontend]
    B -->|WebSocket| C[Backend]
    
    subgraph "Procesamiento del Mensaje"
    C -->|analyze_intent| D[Análisis de Intención]
    D -->|generate_plan| E[Generación de Plan]
    E -->|execute_plan_automatically| F[Ejecución de Plan]
    end
    
    subgraph "Ejecución de Herramientas"
    F -->|execute_step| G[Ejecución de Pasos]
    G -->|execute_core_tool| H[Herramientas Core]
    G -->|execute_mcp_tool| I[Herramientas MCP]
    end
    
    subgraph "Análisis y Expansión"
    G -->|analyze_step_results| J[Análisis de Resultados]
    J -->|should_expand_plan| K[Decisión de Expansión]
    K -->|generate_dynamic_steps| L[Generación de Pasos Dinámicos]
    end
    
    subgraph "Gestión de Memoria"
    C -->|add_conversation| M[Guardar Conversación]
    C -->|update_user_preferences| N[Actualizar Preferencias]
    C -->|learn_from_plan_execution| O[Aprender Patrones]
    M & N & O -->|save_memory_to_disk| P[Persistencia en Disco]
    end
    
    F -->|Outputs| Q[Generación de Outputs]
    Q -->|WebSocket| B
    L -->|WebSocket| B
```

## Detalles de Implementación de Herramientas

### Herramientas Core

```mermaid
classDiagram
    class CoreTools {
        +web_search(query)
        +data_analyzer(data)
        +code_generator(spec)
        +task_planner(description)
    }
```

**Implementación:** [synapse_server_final.py](synapse_server_final.py) - Función `execute_core_tool()`

### Herramientas MCP

```mermaid
classDiagram
    class MCPTools {
        +web_search_mcp(query)
        +github_mcp(query, language)
        +brave_search_mcp(query)
        +... (otras herramientas MCP)
    }
```

**Implementación:** 
- [mcp_integration/real_mcp_tools.py](mcp_integration/real_mcp_tools.py) - Función `execute_real_mcp_tool()`
- Documentación: [CORRECCION_MCP_REALES_FINAL.md](CORRECCION_MCP_REALES_FINAL.md)

## Arquitectura de Componentes

```mermaid
componentDiagram
    component Frontend {
        [App.js]
        [ConversationPanel]
        [PlanningPanel]
        [ToolsPanel]
        [OutputsPanel]
        [MemoryPanel]
        [LLMSelector]
    }
    
    component Backend {
        [synapse_server_final.py]
        [Análisis de Intención]
        [Generación de Plan]
        [Ejecución de Plan]
        [Sistema de Memoria]
        [Configuración LLM]
    }
    
    component Herramientas {
        [Core Tools]
        [MCP Tools]
        [real_mcp_tools.py]
    }
    
    component Análisis {
        [dynamic_analysis.py]
        [output_generators.py]
    }
    
    Frontend --> Backend : WebSocket
    Backend --> Herramientas : Llamadas
    Backend --> Análisis : Llamadas
```

## Arquitectura de la Aplicación

```mermaid
flowchart TD
    subgraph "Frontend (React)"
        A[App.js] --> B[ConversationPanel]
        A --> C[PlanningPanel]
        A --> D[ToolsPanel]
        A --> E[OutputsPanel]
        A --> F[MemoryPanel]
        A --> G[LLMSelector]
        A --> H[DebugPanel]
        I[SynapseContext] --> A
    end

    subgraph "Backend (Flask + SocketIO)"
        J[synapse_server_final.py] --> K[API Endpoints]
        J --> L[WebSocket Handlers]
        J --> M[Sistema de Memoria]
        J --> N[Configuración LLM]
        J --> O[Ejecución de Plan]
        O --> P[Herramientas Core]
        O --> Q[Herramientas MCP]
        J --> R[Análisis Dinámico]
    end

    subgraph "Almacenamiento"
        S[synapse_memory.json]
        T[llm_config.json]
        U[Directorio backups]
    end

    I <-->|WebSocket| L
    I -->|HTTP| K
    M --> S
    N --> T
    M --> U
```

## Comunicación WebSocket

```mermaid
sequenceDiagram
    participant F as Frontend
    participant B as Backend

    F->>B: connect()
    B->>F: connection_status

    F->>B: user_message(message)
    B->>F: message_response(response)

    B->>F: plan_generated(plan)

    loop Para cada paso del plan
        B->>F: plan_step_update(step_id, status, output)
    end

    B->>F: plan_completed(summary)

    F->>B: get_llm_config()
    B->>F: llm_config_response(config)

    F->>B: update_llm_config(config)
    B->>F: llm_config_updated(status)

    F->>B: test_llm_connection(llm_id)
    B->>F: llm_test_result(status)
```

## API REST Endpoints

| Endpoint | Método | Descripción | Implementación |
|----------|---------|-------------|----------------|
| `/api/health` | GET | Estado del servidor | `synapse_server_final.py` |
| `/api/tools` | GET | Lista de herramientas disponibles | `synapse_server_final.py` |
| `/api/memory/all` | GET | Obtener toda la memoria | `synapse_server_final.py` |
| `/api/memory/stats` | GET | Estadísticas de memoria | `synapse_server_final.py` |
| `/api/memory/backup` | POST | Crear backup de memoria | `synapse_server_final.py` |
| `/api/memory/clear` | POST | Limpiar memoria | `synapse_server_final.py` |
| `/api/config` | GET | Obtener configuración | `synapse_server_final.py` |
| `/api/config/llm` | POST | Actualizar configuración LLM | `synapse_server_final.py` |
| `/api/outputs/recent` | GET | Obtener outputs recientes | `synapse_server_final.py` |
| `/api/mcp/tools/:tool_id/execute` | POST | Ejecutar herramienta MCP | `synapse_server_final.py` |

## Despliegue con Docker

```mermaid
flowchart TD
    subgraph "Docker Compose"
        A[docker-compose.yml] --> B[Dockerfile.backend]
        A --> C[Dockerfile.frontend]
    end

    subgraph "Contenedores"
        D[Backend Container] --> F[synapse_server_final.py]
        E[Frontend Container] --> G[Nginx + React Build]
    end

    subgraph "Volúmenes"
        H[synapse_memory.json]
        I[llm_config.json]
    end

    B --> D
    C --> E
    D --> H
    D --> I
```

## Conclusión

Este diagrama de flujo completo muestra la arquitectura y funcionamiento de Synapse, un sistema de agente autónomo que procesa mensajes del usuario, genera planes, ejecuta herramientas, y proporciona resultados detallados. El sistema está compuesto por:

1. **Frontend React**: Interfaz de usuario con paneles especializados para conversación, planificación, herramientas, outputs y memoria.

2. **Backend Flask+SocketIO**: Servidor que maneja la lógica principal, incluyendo análisis de intención, generación de planes, ejecución de herramientas, y gestión de memoria.

3. **Herramientas**: Conjunto de herramientas core (web_search, data_analyzer, code_generator, task_planner) y herramientas MCP (web_search_mcp, github_mcp, brave_search_mcp) que proporcionan funcionalidades especializadas.

4. **Sistema de Memoria**: Almacena conversaciones, preferencias de usuario, patrones aprendidos, y outputs de planes, con persistencia en disco.

5. **Configuración de LLMs**: Permite seleccionar diferentes modelos de lenguaje para cada agente interno (conversación, planificación, ejecución, análisis, memoria, optimización).

6. **Análisis Dinámico**: Analiza los resultados de los pasos y expande los planes dinámicamente según sea necesario.

El sistema utiliza WebSockets para comunicación en tiempo real entre el frontend y el backend, y ofrece una API REST para acceder a diversas funcionalidades. Se despliega utilizando Docker Compose, con contenedores separados para el frontend y el backend.

## Proceso de Ejecución de Herramientas MCP

```mermaid
flowchart TD
    A[execute_mcp_tool] --> B{Herramienta Implementada?}

    B -->|Sí| C{Tipo de Herramienta}
    B -->|No| D[execute_enhanced_simulation]

    C -->|web_search_mcp| E[execute_web_search]
    C -->|github_mcp| F[execute_github_search]
    C -->|brave_search_mcp| G[execute_brave_search]
    C -->|tavily_search| H[execute_tavily_search]
    C -->|firecrawl_mcp| I[execute_firecrawl]

    E --> J{API Key Configurada?}
    G --> K{API Key Configurada?}
    H --> L{API Key Configurada?}
    I --> M{API Key Configurada?}

    J -->|Sí| N[Llamada a DuckDuckGo API]
    J -->|No| O[simulate_web_search]

    K -->|Sí| P[Llamada a Brave API]
    K -->|No| Q[simulate_brave_search]

    L -->|Sí| R[Llamada a Tavily API]
    L -->|No| S[simulate_tavily_search]

    M -->|Sí| T[Llamada a Firecrawl API]
    M -->|No| U[simulate_firecrawl]

    F --> V[Llamada a GitHub API]

    N & P & R & T & V & D & O & Q & S & U --> W[Formatear Resultado]

    W --> X[Retornar Resultado]
```

### Implementación de Herramientas MCP Reales

La implementación de las herramientas MCP reales se encuentra en el archivo `mcp_integration/real_mcp_tools.py`. Cada herramienta tiene su propia función de ejecución que maneja la llamada a la API correspondiente y el procesamiento de los resultados.

#### Ejemplo: Implementación de Web Search MCP

```python
def execute_web_search(parameters):
    """Ejecuta búsqueda web usando DuckDuckGo API"""
    query = parameters.get('query', parameters.get('q', 'synapse ai assistant'))

    try:
        # URL de la API de DuckDuckGo
        url = "https://api.duckduckgo.com/"
        params = {
            'q': query,
            'format': 'json',
            'no_html': '1',
            'skip_disambig': '1'
        }

        # Realizar la solicitud
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        # Formatear resultado
        result_text = f"Resultados de búsqueda para: '{query}'\n\n"

        if data.get('Abstract'):
            result_text += f"Resumen: {data['Abstract']}\n\n"

        if data.get('Definition'):
            result_text += f"Definición: {data['Definition']}\n\n"

        if data.get('RelatedTopics'):
            result_text += "Temas relacionados:\n"
            for i, topic in enumerate(data['RelatedTopics'][:5], 1):
                if 'Text' in topic:
                    result_text += f"{i}. {topic['Text']}\n"

        # Construir resultado
        return {
            'success': True,
            'tool_id': 'web_search_mcp',
            'result': result_text,
            'raw_data': data,
            'execution_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        return {
            'success': False,
            'tool_id': 'web_search_mcp',
            'error': f'Error en búsqueda web: {str(e)}',
            'execution_time': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        }
```

### Integración con el Sistema Principal

Las herramientas MCP se integran con el sistema principal a través de la función `execute_step` en `synapse_server_final.py`, que determina qué herramienta debe ejecutarse para cada paso del plan y llama a la función correspondiente.

```python
def execute_step(step, plan):
    """Ejecuta un paso del plan"""
    # ... código omitido ...

    # Ejecutar herramientas asignadas al paso
    tool_results = []
    if 'tools' in step and step['tools']:
        for tool_id in step['tools']:
            # Obtener parámetros para la herramienta
            tool_params = step.get('tool_parameters', {}).get(tool_id, {})

            # Ejecutar herramienta MCP
            if tool_id in [t['id'] for t in available_tools if t['type'] == 'mcp']:
                tool_result = execute_mcp_tool(tool_id, tool_params)
                tool_results.append(tool_result)

            # Ejecutar herramientas core
            elif tool_id in [t['id'] for t in available_tools if t['type'] == 'core']:
                core_result = execute_core_tool(tool_id, tool_params, step)
                tool_results.append(core_result)

    # ... código omitido ...
```