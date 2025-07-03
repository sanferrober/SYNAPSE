# Synapse Refactored Deployment Script for Windows

Write-Host "🚀 Deploying Synapse Refactored..." -ForegroundColor Green

# Check if Docker is installed
try {
    docker --version | Out-Null
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if Docker Compose is installed
try {
    docker-compose --version | Out-Null
} catch {
    Write-Host "❌ Docker Compose is not installed. Please install Docker Compose first." -ForegroundColor Red
    exit 1
}

# Prepare configuration files
Write-Host "📋 Preparing configuration files..." -ForegroundColor Yellow

# Use migrated config if it exists, otherwise use default
if (Test-Path "synapse_config_migrated.json") {
    Write-Host "✓ Using migrated configuration" -ForegroundColor Green
    Copy-Item "synapse_config_migrated.json" "synapse_config.json" -Force
} elseif (-not (Test-Path "synapse_config.json")) {
    Write-Host "⚠️  No configuration found, creating default..." -ForegroundColor Yellow
    @'
{
    "llm": {
        "conversation_agent": "gemini-1.5-flash",
        "planning_agent": "gemini-1.5-flash",
        "execution_agent": "gemini-1.5-flash",
        "analysis_agent": "gemini-1.5-flash",
        "memory_agent": "gemini-1.5-flash",
        "optimization_agent": "gemini-1.5-flash"
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
'@ | Out-File -FilePath "synapse_config.json" -Encoding UTF8
}

# Use migrated memory if it exists
if (Test-Path "synapse_memory_migrated.json") {
    Write-Host "✓ Using migrated memory" -ForegroundColor Green
    Copy-Item "synapse_memory_migrated.json" "synapse_memory.json" -Force
} elseif (-not (Test-Path "synapse_memory.json")) {
    Write-Host "⚠️  No memory file found, creating empty..." -ForegroundColor Yellow
    '{"conversations": [], "user_preferences": {}, "learned_patterns": [], "plan_outputs": {}, "executed_plans": []}' | Out-File -FilePath "synapse_memory.json" -Encoding UTF8
}

# Stop existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.refactored.yml down

# Build and start containers
Write-Host "🔨 Building and starting containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.refactored.yml up -d --build

# Wait for services to start
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if containers are running
$runningContainers = docker ps | Select-String "synapse-"
if ($runningContainers.Count -eq 2) {
    Write-Host "✅ Deployment successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Access Synapse at:" -ForegroundColor Cyan
    Write-Host "   - Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "   - Backend API: http://localhost:5000" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 View logs with:" -ForegroundColor Yellow
    Write-Host "   docker-compose -f docker-compose.refactored.yml logs -f" -ForegroundColor White
    Write-Host ""
    Write-Host "🛑 Stop services with:" -ForegroundColor Yellow
    Write-Host "   docker-compose -f docker-compose.refactored.yml down" -ForegroundColor White
} else {
    Write-Host "❌ Deployment failed. Check logs with:" -ForegroundColor Red
    Write-Host "   docker-compose -f docker-compose.refactored.yml logs" -ForegroundColor White
    exit 1
}