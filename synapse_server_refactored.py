"""
Synapse Core Server - Refactored main application
"""

import os
import sys
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from synapse_core import Config, MemoryManager, AgentManager
from synapse_core.tools import ToolRegistry
from synapse_core.api import create_api_blueprint
from synapse_core.websocket import WebSocketHandler
from synapse_core.utils import logger, create_success_response


class SynapseServer:
    """Main Synapse server application"""
    
    def __init__(self, config_file: str = None):
        # Initialize configuration
        self.config = Config(config_file)
        
        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = os.urandom(24).hex()
        
        # Initialize CORS
        CORS(self.app, origins=self.config.server.cors_origins)
        
        # Initialize SocketIO
        self.socketio = SocketIO(
            self.app,
            cors_allowed_origins=self.config.server.cors_origins,
            async_mode='threading'
        )
        
        # Initialize components
        self.memory_manager = MemoryManager(self.config)
        self.agent_manager = AgentManager(self.config, self.memory_manager)
        self.tool_registry = ToolRegistry(self.config)
        
        # Initialize WebSocket handler
        self.websocket_handler = WebSocketHandler(
            self.socketio,
            self.config,
            self.memory_manager,
            self.agent_manager,
            self.tool_registry
        )
        
        # Setup routes
        self._setup_routes()
        
        logger.info("Synapse Server initialized successfully")
    
    def _setup_routes(self):
        """Setup Flask routes"""
        # Register API blueprint
        api_blueprint = create_api_blueprint(
            self.config,
            self.memory_manager,
            self.agent_manager,
            self.tool_registry
        )
        self.app.register_blueprint(api_blueprint, url_prefix='/api')
        
        # Serve static files in development
        if self.config.server.debug:
            @self.app.route('/')
            def index():
                return send_from_directory('synapse-ui-new/build', 'index.html')
            
            @self.app.route('/<path:path>')
            def serve_static(path):
                return send_from_directory('synapse-ui-new/build', path)
        
        # Health check endpoint
        @self.app.route('/health')
        def health():
            return create_success_response({
                'status': 'healthy',
                'version': '1.0.0',
                'components': {
                    'memory': self.memory_manager.get_memory_stats(),
                    'agents': len(self.agent_manager.agents),
                    'tools': len(self.tool_registry.tools)
                }
            })
    
    def run(self):
        """Run the server"""
        host = self.config.server.host
        port = self.config.server.port
        debug = self.config.server.debug
        
        logger.info(f"Starting Synapse Server on {host}:{port}")
        logger.info(f"Debug mode: {debug}")
        
        # Run with SocketIO
        self.socketio.run(
            self.app,
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug,
            log_output=debug
        )


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Synapse Core Server')
    parser.add_argument(
        '--config',
        type=str,
        default='synapse_config.json',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--host',
        type=str,
        help='Override host from config'
    )
    parser.add_argument(
        '--port',
        type=int,
        help='Override port from config'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    args = parser.parse_args()
    
    # Create server instance
    server = SynapseServer(args.config)
    
    # Override config if needed
    if args.host:
        server.config.server.host = args.host
    if args.port:
        server.config.server.port = args.port
    if args.debug:
        server.config.server.debug = True
    
    # Run server
    server.run()


if __name__ == '__main__':
    main()