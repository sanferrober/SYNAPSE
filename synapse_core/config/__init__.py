"""
Configuration management for Synapse
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class LLMConfig:
    """Configuration for Language Model agents"""
    conversation_agent: str = "gemini-2.5-flash"
    planning_agent: str = "gemini-2.5-flash"
    execution_agent: str = "gemini-2.5-flash"
    analysis_agent: str = "gemini-2.5-flash"
    memory_agent: str = "gemini-2.5-flash"
    optimization_agent: str = "gemini-2.5-flash"


@dataclass
class ServerConfig:
    """Server configuration"""
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False
    cors_origins: str = "*"


@dataclass
class MemoryConfig:
    """Memory system configuration"""
    persistence_file: str = "synapse_memory.json"
    backup_dir: str = "backups"
    max_conversations: int = 1000
    max_patterns: int = 500


@dataclass
class ToolsConfig:
    """Tools configuration"""
    enable_mcp_tools: bool = True
    enable_core_tools: bool = True
    timeout: int = 30
    max_retries: int = 3


class Config:
    """Main configuration class for Synapse"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "synapse_config.json"
        self.llm = LLMConfig()
        self.server = ServerConfig()
        self.memory = MemoryConfig()
        self.tools = ToolsConfig()
        
        # Environment variables
        self.google_api_key = os.getenv('GOOGLE_API_KEY', '')
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', '')
        self.brave_api_key = os.getenv('BRAVE_API_KEY', 'demo_key')
        self.tavily_api_key = os.getenv('TAVILY_API_KEY', 'demo_key')
        
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file"""
        if Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Load LLM config
                if 'llm' in data:
                    for key, value in data['llm'].items():
                        if hasattr(self.llm, key):
                            setattr(self.llm, key, value)
                
                # Load server config
                if 'server' in data:
                    for key, value in data['server'].items():
                        if hasattr(self.server, key):
                            setattr(self.server, key, value)
                
                # Load memory config
                if 'memory' in data:
                    for key, value in data['memory'].items():
                        if hasattr(self.memory, key):
                            setattr(self.memory, key, value)
                
                # Load tools config
                if 'tools' in data:
                    for key, value in data['tools'].items():
                        if hasattr(self.tools, key):
                            setattr(self.tools, key, value)
                            
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def save_config(self) -> None:
        """Save configuration to file"""
        try:
            config_data = {
                'llm': asdict(self.llm),
                'server': asdict(self.server),
                'memory': asdict(self.memory),
                'tools': asdict(self.tools)
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_llm_for_agent(self, agent_type: str) -> str:
        """Get LLM model for specific agent type"""
        agent_key = f"{agent_type}_agent"
        return getattr(self.llm, agent_key, self.llm.conversation_agent)
    
    def update_llm_config(self, updates: Dict[str, str]) -> None:
        """Update LLM configuration"""
        for key, value in updates.items():
            if hasattr(self.llm, key):
                setattr(self.llm, key, value)
        self.save_config()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'llm': asdict(self.llm),
            'server': asdict(self.server),
            'memory': asdict(self.memory),
            'tools': asdict(self.tools)
        }