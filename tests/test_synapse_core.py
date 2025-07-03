"""
Unit tests for Synapse Core refactored components
"""

import unittest
import json
import tempfile
import os
from datetime import datetime

# Add parent directory to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synapse_core.config import Config, LLMConfig, ServerConfig
from synapse_core.memory import MemoryManager
from synapse_core.agents import AgentManager, ConversationAgent
from synapse_core.tools import ToolRegistry, WebSearchTool
from synapse_core.utils import generate_id, truncate_text, Cache, RateLimiter


class TestConfig(unittest.TestCase):
    """Test configuration management"""
    
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.config = Config(self.temp_file.name)
    
    def tearDown(self):
        os.unlink(self.temp_file.name)
    
    def test_default_config(self):
        """Test default configuration values"""
        self.assertEqual(self.config.llm.conversation_agent, "gemini-1.5-flash")
        self.assertEqual(self.config.server.port, 5000)
        self.assertEqual(self.config.memory.max_conversations, 1000)
        self.assertTrue(self.config.tools.enable_mcp_tools)
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration"""
        # Update config
        self.config.llm.conversation_agent = "gpt-4"
        self.config.save_config()
        
        # Load in new instance
        new_config = Config(self.temp_file.name)
        self.assertEqual(new_config.llm.conversation_agent, "gpt-4")
    
    def test_update_llm_config(self):
        """Test updating LLM configuration"""
        updates = {
            "conversation_agent": "claude-3",
            "planning_agent": "gpt-4"
        }
        self.config.update_llm_config(updates)
        
        self.assertEqual(self.config.llm.conversation_agent, "claude-3")
        self.assertEqual(self.config.llm.planning_agent, "gpt-4")


class TestMemoryManager(unittest.TestCase):
    """Test memory management"""
    
    def setUp(self):
        self.config = Config()
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.config.memory.persistence_file = self.temp_file.name
        self.memory = MemoryManager(self.config)
    
    def tearDown(self):
        os.unlink(self.temp_file.name)
    
    def test_add_conversation(self):
        """Test adding conversations"""
        self.memory.add_conversation("user1", "Hello", "Hi there!")
        conversations = self.memory.get_recent_conversations("user1")
        
        self.assertEqual(len(conversations), 1)
        self.assertEqual(conversations[0]["message"], "Hello")
        self.assertEqual(conversations[0]["response"], "Hi there!")
    
    def test_user_preferences(self):
        """Test user preferences management"""
        prefs = {"language": "es", "style": "formal"}
        self.memory.update_user_preferences("user1", prefs)
        
        retrieved = self.memory.get_user_preferences("user1")
        self.assertEqual(retrieved["language"], "es")
        self.assertEqual(retrieved["style"], "formal")
    
    def test_learned_patterns(self):
        """Test learned patterns"""
        pattern = {
            "type": "query_pattern",
            "pattern": "weather",
            "success_rate": 0.85
        }
        self.memory.add_learned_pattern(pattern)
        
        patterns = self.memory.get_learned_patterns("query_pattern")
        self.assertEqual(len(patterns), 1)
        self.assertEqual(patterns[0]["pattern"], "weather")
    
    def test_memory_persistence(self):
        """Test memory persistence"""
        self.memory.add_conversation("user1", "Test", "Response")
        self.memory.save_memory()
        
        # Create new instance
        new_memory = MemoryManager(self.config)
        conversations = new_memory.get_recent_conversations("user1")
        self.assertEqual(len(conversations), 1)


class TestAgents(unittest.TestCase):
    """Test agent system"""
    
    def setUp(self):
        self.config = Config()
        self.memory = MemoryManager(self.config)
        self.agent_manager = AgentManager(self.config, self.memory)
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        agents = self.agent_manager.get_all_agents_info()
        
        expected_agents = ["conversation", "planning", "execution", "analysis", "memory", "optimization"]
        for agent in expected_agents:
            self.assertIn(agent, agents)
    
    def test_conversation_agent(self):
        """Test conversation agent"""
        result = self.agent_manager.process_with_agent("conversation", {
            "message": "Hello",
            "context": {},
            "timestamp": datetime.now().isoformat()
        })
        
        self.assertIn("response", result)
        self.assertIn("metadata", result)
    
    def test_planning_agent(self):
        """Test planning agent"""
        result = self.agent_manager.process_with_agent("planning", {
            "intent": {"type": "search", "query": "test"},
            "context": {}
        })
        
        self.assertIn("plan", result)
        self.assertIn("steps", result["plan"])


class TestTools(unittest.TestCase):
    """Test tools system"""
    
    def setUp(self):
        self.config = Config()
        self.tool_registry = ToolRegistry(self.config)
    
    def test_tool_registration(self):
        """Test tool registration"""
        tools = self.tool_registry.get_all_tools()
        self.assertGreater(len(tools), 0)
        
        # Check for core tools
        tool_ids = [t["id"] for t in tools]
        self.assertIn("web_search", tool_ids)
        self.assertIn("data_analyzer", tool_ids)
    
    def test_tool_execution(self):
        """Test tool execution"""
        result = self.tool_registry.execute_tool("web_search", {
            "query": "test query"
        })
        
        self.assertTrue(result["success"])
        self.assertIn("results", result)
    
    def test_tool_enable_disable(self):
        """Test enabling and disabling tools"""
        self.tool_registry.disable_tool("web_search")
        tool = self.tool_registry.get_tool("web_search")
        self.assertFalse(tool.enabled)
        
        self.tool_registry.enable_tool("web_search")
        self.assertTrue(tool.enabled)


class TestUtils(unittest.TestCase):
    """Test utility functions"""
    
    def test_generate_id(self):
        """Test ID generation"""
        id1 = generate_id("test_")
        id2 = generate_id("test_")
        
        self.assertTrue(id1.startswith("test_"))
        self.assertNotEqual(id1, id2)
    
    def test_truncate_text(self):
        """Test text truncation"""
        text = "This is a very long text that needs to be truncated"
        truncated = truncate_text(text, 20)
        
        self.assertEqual(len(truncated), 20)
        self.assertTrue(truncated.endswith("..."))
    
    def test_cache(self):
        """Test cache functionality"""
        cache = Cache(ttl=1)
        
        cache.set("key1", "value1")
        self.assertEqual(cache.get("key1"), "value1")
        
        # Test TTL
        import time
        time.sleep(1.1)
        self.assertIsNone(cache.get("key1"))
    
    def test_rate_limiter(self):
        """Test rate limiter"""
        limiter = RateLimiter(max_calls=2, time_window=1)
        
        self.assertTrue(limiter.is_allowed("user1"))
        self.assertTrue(limiter.is_allowed("user1"))
        self.assertFalse(limiter.is_allowed("user1"))  # Should be limited


if __name__ == '__main__':
    unittest.main()