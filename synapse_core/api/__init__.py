"""
API routes for Synapse
"""

from flask import Blueprint, jsonify, request
from typing import Dict, Any
import json


def create_api_blueprint(config, memory_manager, agent_manager, tool_registry):
    """Create API blueprint with all routes"""
    
    api = Blueprint('api', __name__, url_prefix='/api')
    
    @api.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "version": "1.0.0",
            "service": "Synapse Core"
        })
    
    @api.route('/config', methods=['GET'])
    def get_config():
        """Get current configuration"""
        return jsonify(config.to_dict())
    
    @api.route('/config/llm', methods=['POST'])
    def update_llm_config():
        """Update LLM configuration"""
        try:
            updates = request.json
            config.update_llm_config(updates)
            return jsonify({
                "success": True,
                "message": "LLM configuration updated",
                "config": config.llm.__dict__
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 400
    
    # Memory endpoints
    @api.route('/memory/stats', methods=['GET'])
    def get_memory_stats():
        """Get memory statistics"""
        return jsonify(memory_manager.get_memory_stats())
    
    @api.route('/memory/conversations', methods=['GET'])
    def get_conversations():
        """Get recent conversations"""
        user_id = request.args.get('user_id')
        limit = int(request.args.get('limit', 10))
        
        conversations = memory_manager.get_recent_conversations(user_id, limit)
        return jsonify({
            "conversations": conversations,
            "total": len(conversations)
        })
    
    @api.route('/memory/preferences/<user_id>', methods=['GET'])
    def get_user_preferences(user_id):
        """Get user preferences"""
        preferences = memory_manager.get_user_preferences(user_id)
        return jsonify({
            "user_id": user_id,
            "preferences": preferences
        })
    
    @api.route('/memory/patterns', methods=['GET'])
    def get_patterns():
        """Get learned patterns"""
        pattern_type = request.args.get('type')
        patterns = memory_manager.get_learned_patterns(pattern_type)
        return jsonify({
            "patterns": patterns,
            "total": len(patterns)
        })
    
    @api.route('/memory/backup', methods=['POST'])
    def create_backup():
        """Create memory backup"""
        try:
            backup_file = memory_manager.create_backup()
            return jsonify({
                "success": True,
                "backup_file": backup_file
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @api.route('/memory/clear', methods=['POST'])
    def clear_memory():
        """Clear all memory"""
        try:
            memory_manager.clear_memory()
            return jsonify({
                "success": True,
                "message": "Memory cleared successfully"
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @api.route('/memory/search', methods=['POST'])
    def search_memory():
        """Search in memory"""
        data = request.json
        query = data.get('query', '')
        user_id = data.get('user_id')
        
        results = memory_manager.search_conversations(query, user_id)
        return jsonify({
            "results": results,
            "total": len(results),
            "query": query
        })
    
    # Agent endpoints
    @api.route('/agents', methods=['GET'])
    def get_agents():
        """Get all agents information"""
        return jsonify(agent_manager.get_all_agents_info())
    
    @api.route('/agents/<agent_type>/process', methods=['POST'])
    def process_with_agent(agent_type):
        """Process input with specific agent"""
        try:
            input_data = request.json
            result = agent_manager.process_with_agent(agent_type, input_data)
            
            if "error" in result:
                return jsonify(result), 400
            
            return jsonify(result)
        except Exception as e:
            return jsonify({
                "error": str(e),
                "agent": agent_type
            }), 500
    
    # Tool endpoints
    @api.route('/tools', methods=['GET'])
    def get_tools():
        """Get all available tools"""
        category = request.args.get('category')
        
        if category:
            tools = tool_registry.get_tools_by_category(category)
        else:
            tools = tool_registry.get_all_tools()
        
        return jsonify({
            "tools": tools,
            "total": len(tools)
        })
    
    @api.route('/tools/<tool_id>', methods=['GET'])
    def get_tool(tool_id):
        """Get specific tool information"""
        tool = tool_registry.get_tool(tool_id)
        
        if not tool:
            return jsonify({
                "error": f"Tool {tool_id} not found"
            }), 404
        
        return jsonify(tool.to_dict())
    
    @api.route('/tools/<tool_id>/execute', methods=['POST'])
    def execute_tool(tool_id):
        """Execute a tool"""
        try:
            parameters = request.json or {}
            result = tool_registry.execute_tool(tool_id, parameters)
            
            if not result.get("success", False):
                return jsonify(result), 400
            
            return jsonify(result)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e),
                "tool_id": tool_id
            }), 500
    
    @api.route('/tools/<tool_id>/enable', methods=['POST'])
    def enable_tool(tool_id):
        """Enable a tool"""
        success = tool_registry.enable_tool(tool_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Tool {tool_id} enabled"
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Tool {tool_id} not found"
            }), 404
    
    @api.route('/tools/<tool_id>/disable', methods=['POST'])
    def disable_tool(tool_id):
        """Disable a tool"""
        success = tool_registry.disable_tool(tool_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Tool {tool_id} disabled"
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Tool {tool_id} not found"
            }), 404
    
    # System endpoints
    @api.route('/system/status', methods=['GET'])
    def system_status():
        """Get system status"""
        memory_stats = memory_manager.get_memory_stats()
        
        return jsonify({
            "status": "operational",
            "memory": memory_stats,
            "agents": {
                "total": len(agent_manager.agents),
                "active": len([a for a in agent_manager.agents.values() if a])
            },
            "tools": {
                "total": len(tool_registry.tools),
                "enabled": len([t for t in tool_registry.tools.values() if t.enabled])
            }
        })
    
    return api