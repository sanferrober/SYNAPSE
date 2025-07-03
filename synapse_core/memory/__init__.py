"""
Memory management system for Synapse
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import threading


class MemoryManager:
    """Manages persistent memory for Synapse"""
    
    def __init__(self, config):
        self.config = config
        self.memory_file = config.memory.persistence_file
        self.backup_dir = config.memory.backup_dir
        self.lock = threading.Lock()
        
        # Memory structure
        self.memory_store = {
            "conversations": [],
            "user_preferences": {},
            "learned_patterns": [],
            "plan_outputs": {},
            "executed_plans": []
        }
        
        self._ensure_directories()
        self.load_memory()
    
    def _ensure_directories(self) -> None:
        """Ensure required directories exist"""
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)
    
    def load_memory(self) -> None:
        """Load memory from disk"""
        with self.lock:
            if Path(self.memory_file).exists():
                try:
                    with open(self.memory_file, 'r', encoding='utf-8') as f:
                        loaded_data = json.load(f)
                        # Merge with default structure
                        for key in self.memory_store:
                            if key in loaded_data:
                                self.memory_store[key] = loaded_data[key]
                except Exception as e:
                    print(f"Error loading memory: {e}")
    
    def save_memory(self) -> None:
        """Save memory to disk"""
        with self.lock:
            try:
                with open(self.memory_file, 'w', encoding='utf-8') as f:
                    json.dump(self.memory_store, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Error saving memory: {e}")
    
    def add_conversation(self, user_id: str, message: str, response: str, 
                        metadata: Optional[Dict] = None) -> None:
        """Add a conversation to memory"""
        with self.lock:
            conversation = {
                "id": f"conv_{datetime.now().timestamp()}",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "message": message,
                "response": response,
                "metadata": metadata or {}
            }
            
            self.memory_store["conversations"].append(conversation)
            
            # Limit conversations
            if len(self.memory_store["conversations"]) > self.config.memory.max_conversations:
                self.memory_store["conversations"] = \
                    self.memory_store["conversations"][-self.config.memory.max_conversations:]
            
            self.save_memory()
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> None:
        """Update user preferences"""
        with self.lock:
            if user_id not in self.memory_store["user_preferences"]:
                self.memory_store["user_preferences"][user_id] = {
                    "created_at": datetime.now().isoformat(),
                    "preferences": {}
                }
            
            self.memory_store["user_preferences"][user_id]["preferences"].update(preferences)
            self.memory_store["user_preferences"][user_id]["updated_at"] = datetime.now().isoformat()
            
            self.save_memory()
    
    def add_learned_pattern(self, pattern: Dict[str, Any]) -> None:
        """Add a learned pattern"""
        with self.lock:
            pattern["id"] = f"pattern_{datetime.now().timestamp()}"
            pattern["created_at"] = datetime.now().isoformat()
            
            self.memory_store["learned_patterns"].append(pattern)
            
            # Limit patterns
            if len(self.memory_store["learned_patterns"]) > self.config.memory.max_patterns:
                # Keep most successful patterns
                self.memory_store["learned_patterns"].sort(
                    key=lambda x: x.get("success_rate", 0), 
                    reverse=True
                )
                self.memory_store["learned_patterns"] = \
                    self.memory_store["learned_patterns"][:self.config.memory.max_patterns]
            
            self.save_memory()
    
    def add_plan_output(self, plan_id: str, step_id: str, output: str) -> None:
        """Add output for a plan step"""
        with self.lock:
            if plan_id not in self.memory_store["plan_outputs"]:
                self.memory_store["plan_outputs"][plan_id] = {}
            
            self.memory_store["plan_outputs"][plan_id][step_id] = {
                "output": output,
                "timestamp": datetime.now().isoformat()
            }
            
            self.save_memory()
    
    def add_executed_plan(self, plan: Dict[str, Any]) -> None:
        """Add an executed plan to memory"""
        with self.lock:
            plan["executed_at"] = datetime.now().isoformat()
            self.memory_store["executed_plans"].append(plan)
            self.save_memory()
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences"""
        with self.lock:
            return self.memory_store["user_preferences"].get(user_id, {}).get("preferences", {})
    
    def get_recent_conversations(self, user_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get recent conversations"""
        with self.lock:
            conversations = self.memory_store["conversations"]
            
            if user_id:
                conversations = [c for c in conversations if c.get("user_id") == user_id]
            
            return conversations[-limit:]
    
    def get_learned_patterns(self, pattern_type: Optional[str] = None) -> List[Dict]:
        """Get learned patterns"""
        with self.lock:
            patterns = self.memory_store["learned_patterns"]
            
            if pattern_type:
                patterns = [p for p in patterns if p.get("type") == pattern_type]
            
            return patterns
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        with self.lock:
            return {
                "total_conversations": len(self.memory_store["conversations"]),
                "total_users": len(self.memory_store["user_preferences"]),
                "total_patterns": len(self.memory_store["learned_patterns"]),
                "total_plans": len(self.memory_store["executed_plans"]),
                "memory_size_bytes": os.path.getsize(self.memory_file) if Path(self.memory_file).exists() else 0
            }
    
    def create_backup(self) -> str:
        """Create a backup of current memory"""
        with self.lock:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = Path(self.backup_dir) / f"memory_backup_{timestamp}.json"
            
            try:
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(self.memory_store, f, indent=2, ensure_ascii=False)
                return str(backup_file)
            except Exception as e:
                raise Exception(f"Error creating backup: {e}")
    
    def clear_memory(self) -> None:
        """Clear all memory"""
        with self.lock:
            self.memory_store = {
                "conversations": [],
                "user_preferences": {},
                "learned_patterns": [],
                "plan_outputs": {},
                "executed_plans": []
            }
            self.save_memory()
    
    def search_conversations(self, query: str, user_id: Optional[str] = None) -> List[Dict]:
        """Search conversations by query"""
        with self.lock:
            results = []
            query_lower = query.lower()
            
            for conv in self.memory_store["conversations"]:
                if user_id and conv.get("user_id") != user_id:
                    continue
                
                if (query_lower in conv.get("message", "").lower() or 
                    query_lower in conv.get("response", "").lower()):
                    results.append(conv)
            
            return results