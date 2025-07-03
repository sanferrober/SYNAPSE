#!/usr/bin/env python3
"""
Migration script from old Synapse structure to refactored version
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime


class SynapseMigration:
    """Handles migration from old to new Synapse structure"""
    
    def __init__(self):
        self.migration_log = []
        self.backup_dir = f"migration_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def log(self, message: str, level: str = "INFO"):
        """Log migration message"""
        entry = f"[{level}] {datetime.now().isoformat()} - {message}"
        self.migration_log.append(entry)
        print(entry)
    
    def create_backup(self):
        """Create backup of current files"""
        self.log("Creating backup...")
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Files to backup
        files_to_backup = [
            "synapse_server_final.py",
            "synapse_memory.json",
            "llm_config.json",
            "requirements.txt"
        ]
        
        for file in files_to_backup:
            if os.path.exists(file):
                shutil.copy2(file, self.backup_dir)
                self.log(f"Backed up {file}")
    
    def migrate_memory(self):
        """Migrate memory data to new format"""
        self.log("Migrating memory data...")
        
        if os.path.exists("synapse_memory.json"):
            try:
                with open("synapse_memory.json", 'r', encoding='utf-8') as f:
                    old_memory = json.load(f)
                
                # The memory format should be compatible
                # Just ensure all required keys exist
                new_memory = {
                    "conversations": old_memory.get("conversations", []),
                    "user_preferences": old_memory.get("user_preferences", {}),
                    "learned_patterns": old_memory.get("learned_patterns", []),
                    "plan_outputs": old_memory.get("plan_outputs", {}),
                    "executed_plans": old_memory.get("executed_plans", [])
                }
                
                # Save in new format
                with open("synapse_memory_migrated.json", 'w', encoding='utf-8') as f:
                    json.dump(new_memory, f, indent=2, ensure_ascii=False)
                
                self.log("Memory data migrated successfully")
                
            except Exception as e:
                self.log(f"Error migrating memory: {str(e)}", "ERROR")
    
    def migrate_config(self):
        """Migrate configuration to new format"""
        self.log("Migrating configuration...")
        
        # Start with default config
        new_config = {
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
                "debug": False,
                "cors_origins": "*"
            },
            "memory": {
                "persistence_file": "synapse_memory.json",
                "backup_dir": "backups",
                "max_conversations": 1000,
                "max_patterns": 500
            },
            "tools": {
                "enable_mcp_tools": True,
                "enable_core_tools": True,
                "timeout": 30,
                "max_retries": 3
            }
        }
        
        # Try to load old LLM config
        if os.path.exists("llm_config.json"):
            try:
                with open("llm_config.json", 'r', encoding='utf-8') as f:
                    old_llm_config = json.load(f)
                
                # Map old config to new format
                for key, value in old_llm_config.items():
                    if key in new_config["llm"]:
                        new_config["llm"][key] = value
                
                self.log("LLM configuration migrated")
                
            except Exception as e:
                self.log(f"Error migrating LLM config: {str(e)}", "WARNING")
        
        # Save new config
        with open("synapse_config_migrated.json", 'w', encoding='utf-8') as f:
            json.dump(new_config, f, indent=2, ensure_ascii=False)
        
        self.log("Configuration migrated successfully")
    
    def update_requirements(self):
        """Update requirements.txt for new structure"""
        self.log("Updating requirements...")
        
        # Essential requirements for refactored version
        requirements = [
            "flask>=3.0.0",
            "flask-cors>=4.0.0",
            "flask-socketio>=5.3.6",
            "python-socketio>=5.10.0",
            "requests>=2.31.0",
            "psutil>=5.9.6",
            "python-dotenv>=1.0.0"
        ]
        
        # Add any additional requirements from old file
        if os.path.exists("requirements.txt"):
            with open("requirements.txt", 'r') as f:
                old_requirements = f.read().splitlines()
            
            # Merge requirements
            for req in old_requirements:
                if req and not any(req.startswith(r.split('>=')[0]) for r in requirements):
                    requirements.append(req)
        
        # Save new requirements
        with open("requirements_refactored.txt", 'w') as f:
            f.write('\n'.join(requirements))
        
        self.log("Requirements updated")
    
    def create_migration_report(self):
        """Create a migration report"""
        self.log("Creating migration report...")
        
        report = {
            "migration_date": datetime.now().isoformat(),
            "backup_directory": self.backup_dir,
            "files_created": [
                "synapse_config_migrated.json",
                "synapse_memory_migrated.json",
                "requirements_refactored.txt"
            ],
            "next_steps": [
                "1. Review the migrated configuration in synapse_config_migrated.json",
                "2. Test the refactored server with: python synapse_server_refactored.py --config synapse_config_migrated.json",
                "3. If everything works, rename migrated files to remove '_migrated' suffix",
                "4. Update your deployment scripts to use synapse_server_refactored.py",
                "5. Update frontend to use new API endpoints if needed"
            ],
            "migration_log": self.migration_log
        }
        
        with open("migration_report.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log("Migration report created: migration_report.json")
    
    def run(self):
        """Run the complete migration"""
        print("=" * 60)
        print("Synapse Migration Tool")
        print("=" * 60)
        
        self.log("Starting migration process...")
        
        # Step 1: Create backup
        self.create_backup()
        
        # Step 2: Migrate memory
        self.migrate_memory()
        
        # Step 3: Migrate configuration
        self.migrate_config()
        
        # Step 4: Update requirements
        self.update_requirements()
        
        # Step 5: Create report
        self.create_migration_report()
        
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Review migration_report.json for details")
        print("2. Test the refactored server")
        print("3. Update your deployment configuration")
        print(f"\nBackup created in: {self.backup_dir}")


if __name__ == "__main__":
    migration = SynapseMigration()
    migration.run()