from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pathlib import Path
from typing import Dict, Any

from compiler.core import Compiler
from compiler.config import ConfigLoader
from compiler.exceptions import CompilerError

def create_app(config_path: str = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)
    
    # Load configuration
    config = ConfigLoader(config_path)
    app.config.update(config.get_web_config())
    
    # Initialize compiler
    compiler = Compiler(config)
    
    @app.route("/")
    def index() -> str:
        """Render the main page."""
        return render_template("index.html")
        
    @app.route("/api/compile", methods=["POST"])
    def compile_code() -> Dict[str, Any]:
        """Compile source code."""
        try:
            data = request.get_json()
            if not data or "code" not in data:
                return jsonify({
                    "success": False,
                    "error": "No code provided"
                }), 400
                
            # Create temporary file
            temp_file = Path("temp.c")
            with open(temp_file, "w") as f:
                f.write(data["code"])
                
            # Compile
            result = compiler.compile(temp_file)
            
            # Clean up
            temp_file.unlink()
            
            return jsonify({
                "success": True,
                "result": result
            })
            
        except CompilerError as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 400
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Internal server error: {str(e)}"
            }), 500
            
    @app.route("/api/config", methods=["GET", "POST"])
    def handle_config() -> Dict[str, Any]:
        """Get or update configuration."""
        try:
            if request.method == "GET":
                return jsonify({
                    "success": True,
                    "config": compiler.get_config()
                })
                
            data = request.get_json()
            if not data:
                return jsonify({
                    "success": False,
                    "error": "No configuration provided"
                }), 400
                
            compiler.update_config(data)
            return jsonify({
                "success": True,
                "message": "Configuration updated"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 400
            
    @app.route("/api/plugins", methods=["GET"])
    def get_plugins() -> Dict[str, Any]:
        """Get information about available plugins."""
        try:
            return jsonify({
                "success": True,
                "plugins": compiler.get_available_plugins()
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
            
    @app.route("/api/plugins/<plugin_name>/enable", methods=["POST"])
    def enable_plugin(plugin_name: str) -> Dict[str, Any]:
        """Enable a plugin."""
        try:
            compiler.plugin_manager.enable_plugin(plugin_name)
            return jsonify({
                "success": True,
                "message": f"Plugin {plugin_name} enabled"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 400
            
    @app.route("/api/plugins/<plugin_name>/disable", methods=["POST"])
    def disable_plugin(plugin_name: str) -> Dict[str, Any]:
        """Disable a plugin."""
        try:
            compiler.plugin_manager.disable_plugin(plugin_name)
            return jsonify({
                "success": True,
                "message": f"Plugin {plugin_name} disabled"
            })
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 400
            
    return app 