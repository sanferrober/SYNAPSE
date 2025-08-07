#!/bin/bash

echo "🚀 Deploying Synapse Refactored..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Prepare configuration files
echo "📋 Preparing configuration files..."

# Use migrated config if it exists, otherwise use default
if [ -f "synapse_config_migrated.json" ]; then
    echo "✓ Using migrated configuration"
    cp synapse_config_migrated.json synapse_config.json
elif [ ! -f "synapse_config.json" ]; then
    echo "⚠️  No configuration found, creating default..."
    cat > synapse_config.json << 'EOF'
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
        "persistence_file": "/app/data/synapse_memory.json",
        "backup_dir": "/app/data/backups",
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
EOF
fi

# Use migrated memory if it exists
if [ -f "synapse_memory_migrated.json" ]; then
    echo "✓ Using migrated memory"
    cp synapse_memory_migrated.json synapse_memory.json
elif [ ! -f "synapse_memory.json" ]; then
    echo "⚠️  No memory file found, creating empty..."
    echo '{"conversations": [], "user_preferences": {}, "learned_patterns": [], "plan_outputs": {}, "executed_plans": []}' > synapse_memory.json
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.refactored.yml down

# Build and start containers
echo "🔨 Building and starting containers..."
docker-compose -f docker-compose.refactored.yml up -d --build

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check if containers are running
if [ $(docker ps | grep -c "synapse-") -eq 2 ]; then
    echo "✅ Deployment successful!"
    echo ""
    echo "🌐 Access Synapse at:"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Backend API: http://localhost:5000"
    echo ""
    echo "📊 View logs with:"
    echo "   docker-compose -f docker-compose.refactored.yml logs -f"
    echo ""
    echo "🛑 Stop services with:"
    echo "   docker-compose -f docker-compose.refactored.yml down"
else
    echo "❌ Deployment failed. Check logs with:"
    echo "   docker-compose -f docker-compose.refactored.yml logs"
    exit 1
fi