# Synapse Core - Refactored Architecture

## Overview

This is the refactored version of Synapse Core, designed with improved modularity, scalability, and maintainability. The new architecture separates concerns into distinct modules while maintaining backward compatibility.

## 🏗️ Architecture

```
synapse_core/
├── __init__.py          # Core exports
├── config/              # Configuration management
├── agents/              # Agent implementations
├── tools/               # Tool registry and implementations
├── memory/              # Memory management system
├── api/                 # REST API endpoints
├── websocket/           # WebSocket handlers
└── utils/               # Utility functions
```

## 🚀 Quick Start

### Local Development

1. **Test the structure:**
   ```bash
   python test_refactored_structure.py
   ```

2. **Run the server:**
   ```bash
   python synapse_server_refactored.py
   ```

3. **Test endpoints:**
   ```bash
   python test_refactored_server.py
   ```

### Docker Deployment

1. **Deploy with Docker Compose:**
   ```bash
   # Linux/Mac
   ./deploy-refactored.sh
   
   # Windows
   .\deploy-refactored.ps1
   ```

2. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## 📋 Configuration

The refactored version uses a structured configuration system:

```json
{
    "llm": {
        "conversation_agent": "gemini-2.5-flash",
        "planning_agent": "gemini-2.5-flash",
        "execution_agent": "gemini-2.5-flash",
        "analysis_agent": "gemini-2.5-flash",
        "memory_agent": "gemini-2.5-flash",
        "optimization_agent": "gemini-2.5-flash"
    },
    "server": {
        "host": "0.0.0.0",
        "port": 5000,
        "debug": false,
        "cors_origins": ["*"]
    },
    "memory": {
        "persistence_file": "synapse_memory.json",
        "backup_dir": "backups",
        "max_conversations": 1000,
        "max_patterns": 500
    },
    "tools": {
        "mcp_enabled": true,
        "core_enabled": true,
        "timeout": 30,
        "max_retries": 3
    }
}
```

## 🔧 Key Improvements

### 1. **Modular Architecture**
- Clear separation of concerns
- Each module has a single responsibility
- Easy to extend and maintain

### 2. **Centralized Configuration**
- All configuration in one place
- Type-safe configuration with dataclasses
- Environment variable support

### 3. **Improved Memory Management**
- Thread-safe operations
- Automatic persistence
- Backup functionality

### 4. **Enhanced API Design**
- RESTful endpoints
- Consistent response format
- Comprehensive error handling

### 5. **Better Testing**
- Unit tests for each module
- Integration tests
- Test utilities included

## 📚 API Endpoints

### Health & Status
- `GET /api/health` - Server health check
- `GET /api/config` - Get current configuration
- `GET /api/memory/stats` - Memory statistics

### Agents & Tools
- `GET /api/agents` - List all agents
- `GET /api/tools` - List all tools
- `POST /api/tools/execute` - Execute a tool

### Configuration
- `POST /api/config/llm` - Update LLM configuration
- `GET /api/config/llm` - Get LLM configuration

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Test the refactored structure
python test_refactored_structure.py

# Test the server endpoints
python test_refactored_server.py

# Run unit tests
python test_synapse_core.py
```

## 🔄 Migration from Old Version

If you have an existing Synapse installation:

1. **Run the migration script:**
   ```bash
   python migrate_synapse.py
   ```

2. **Deploy the refactored version:**
   ```bash
   ./deploy-refactored.sh
   ```

The migration script will:
- Backup your existing data
- Convert configurations to the new format
- Migrate memory data
- Update dependencies

## 📦 Dependencies

The refactored version maintains the same core dependencies:
- Flask & Flask-CORS
- Flask-SocketIO
- psutil
- requests

See `requirements.txt` for the complete list.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.