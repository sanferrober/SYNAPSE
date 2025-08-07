#!/usr/bin/env python3
"""
Test script for the refactored Synapse server
"""

import requests
import json
import sys
import time

def test_server(base_url="http://localhost:5000"):
    """Test the refactored server endpoints"""
    
    print("Testing Refactored Synapse Server")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test 1: Health check
    print("\n1. Testing /api/health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ Health check passed")
            print(f"  - Status: {data.get('status')}")
            print(f"  - Version: {data.get('version')}")
            if 'data' in data and 'components' in data['data']:
                components = data['data']['components']
                print(f"  - Memory stats: {components.get('memory', {})}")
                print(f"  - Agents loaded: {components.get('agents', 0)}")
                print(f"  - Tools loaded: {components.get('tools', 0)}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
            all_tests_passed = False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        all_tests_passed = False
    
    # Test 2: Configuration endpoint
    print("\n2. Testing /api/config endpoint...")
    try:
        response = requests.get(f"{base_url}/api/config", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ Config endpoint passed")
            if 'data' in data:
                config = data['data']
                print(f"  - LLM config: {list(config.get('llm', {}).keys())}")
                print(f"  - Server config: {config.get('server', {})}")
        else:
            print(f"✗ Config endpoint failed: {response.status_code}")
            all_tests_passed = False
    except Exception as e:
        print(f"✗ Config endpoint error: {e}")
        all_tests_passed = False
    
    # Test 3: Memory stats endpoint
    print("\n3. Testing /api/memory/stats endpoint...")
    try:
        response = requests.get(f"{base_url}/api/memory/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ Memory stats endpoint passed")
            if 'data' in data:
                stats = data['data']
                print(f"  - Conversations: {stats.get('conversations', 0)}")
                print(f"  - Users: {stats.get('users', 0)}")
                print(f"  - Patterns: {stats.get('patterns', 0)}")
        else:
            print(f"✗ Memory stats failed: {response.status_code}")
            all_tests_passed = False
    except Exception as e:
        print(f"✗ Memory stats error: {e}")
        all_tests_passed = False
    
    # Test 4: Agents endpoint
    print("\n4. Testing /api/agents endpoint...")
    try:
        response = requests.get(f"{base_url}/api/agents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ Agents endpoint passed")
            if 'data' in data:
                agents = data['data']
                print(f"  - Total agents: {len(agents)}")
                for agent in agents[:3]:  # Show first 3 agents
                    print(f"  - {agent.get('name')}: {agent.get('type')}")
        else:
            print(f"✗ Agents endpoint failed: {response.status_code}")
            all_tests_passed = False
    except Exception as e:
        print(f"✗ Agents endpoint error: {e}")
        all_tests_passed = False
    
    # Test 5: Tools endpoint
    print("\n5. Testing /api/tools endpoint...")
    try:
        response = requests.get(f"{base_url}/api/tools", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ Tools endpoint passed")
            if 'data' in data:
                tools = data['data']
                print(f"  - Total tools: {len(tools)}")
                # Show tool categories
                categories = {}
                for tool in tools:
                    cat = tool.get('category', 'unknown')
                    categories[cat] = categories.get(cat, 0) + 1
                for cat, count in categories.items():
                    print(f"  - {cat}: {count} tools")
        else:
            print(f"✗ Tools endpoint failed: {response.status_code}")
            all_tests_passed = False
    except Exception as e:
        print(f"✗ Tools endpoint error: {e}")
        all_tests_passed = False
    
    # Test 6: LLM configuration update
    print("\n6. Testing LLM configuration update...")
    try:
        test_config = {
            "conversation_agent": "gemini-2.5-flash",
            "planning_agent": "gemini-2.5-flash"
        }
        response = requests.post(
            f"{base_url}/api/config/llm",
            json=test_config,
            timeout=5
        )
        if response.status_code == 200:
            print("✓ LLM config update passed")
            data = response.json()
            if 'data' in data:
                print(f"  - Updated config: {data['data']}")
        else:
            print(f"✗ LLM config update failed: {response.status_code}")
            all_tests_passed = False
    except Exception as e:
        print(f"✗ LLM config update error: {e}")
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("✅ All tests passed!")
        print("\nThe refactored server is working correctly.")
    else:
        print("❌ Some tests failed!")
        print("\nPlease check the server logs for more details.")
    
    return all_tests_passed

if __name__ == "__main__":
    # Check if a custom URL was provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    # First check if server is running
    print(f"Checking if server is running at {base_url}...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=2)
        print("✓ Server is running")
    except:
        print("✗ Server is not running")
        print(f"\nPlease start the server with:")
        print("  python synapse_server_refactored.py")
        sys.exit(1)
    
    # Run tests
    success = test_server(base_url)
    sys.exit(0 if success else 1)