#!/usr/bin/env python3
"""
Simple test to verify refactored structure
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all imports work correctly"""
    print("Testing imports...")
    
    try:
        from synapse_core import Config, MemoryManager, AgentManager
        print("✓ Core imports successful")
    except Exception as e:
        print(f"✗ Core imports failed: {e}")
        return False
    
    try:
        from synapse_core.tools import ToolRegistry
        print("✓ Tools import successful")
    except Exception as e:
        print(f"✗ Tools import failed: {e}")
        return False
    
    try:
        from synapse_core.api import create_api_blueprint
        print("✓ API import successful")
    except Exception as e:
        print(f"✗ API import failed: {e}")
        return False
    
    try:
        from synapse_core.websocket import WebSocketHandler
        print("✓ WebSocket import successful")
    except Exception as e:
        print(f"✗ WebSocket import failed: {e}")
        return False
    
    try:
        from synapse_core.utils import logger, create_success_response
        print("✓ Utils import successful")
    except Exception as e:
        print(f"✗ Utils import failed: {e}")
        return False
    
    return True

def test_initialization():
    """Test if components can be initialized"""
    print("\nTesting initialization...")
    
    try:
        from synapse_core import Config
        config = Config()
        print("✓ Config initialized")
        print(f"  - Server host: {config.server.host}")
        print(f"  - Server port: {config.server.port}")
    except Exception as e:
        print(f"✗ Config initialization failed: {e}")
        return False
    
    try:
        from synapse_core import MemoryManager
        memory = MemoryManager(config)
        print("✓ MemoryManager initialized")
        stats = memory.get_memory_stats()  # Changed from get_stats
        print(f"  - Conversations: {stats.get('conversations', 0)}")
    except Exception as e:
        print(f"✗ MemoryManager initialization failed: {e}")
        return False
    
    try:
        from synapse_core import AgentManager
        agents = AgentManager(config, memory)
        print("✓ AgentManager initialized")
        print(f"  - Agents loaded: {len(agents.agents)}")
    except Exception as e:
        print(f"✗ AgentManager initialization failed: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("Synapse Refactored Structure Test")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n✗ Import tests failed!")
        return 1
    
    # Test initialization
    if not test_initialization():
        print("\n✗ Initialization tests failed!")
        return 1
    
    print("\n" + "=" * 50)
    print("✓ All tests passed!")
    print("\nThe refactored structure is working correctly.")
    print("You can now run: python synapse_server_refactored.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())