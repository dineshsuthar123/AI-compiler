from flask import Flask, render_template, request, jsonify, send_file
from simple_compiler import ModernCompiler
import logging
import json
import time
import os
import sys
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
from datetime import datetime
import tempfile
import uuid
import threading
from pathlib import Path

app = Flask(__name__)
compiler = ModernCompiler()
start_time = time.time()  # Track application start time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store compilation history and active sessions
compilation_history = []
active_sessions = {}
real_time_stats = {
    'cpu_usage': 0,
    'memory_usage': 0,
    'active_compilations': 0,
    'total_lines_compiled': 0
}

# Performance monitoring
def update_system_stats():
    """Update real-time system statistics"""
    while True:
        try:
            if PSUTIL_AVAILABLE:
                real_time_stats['cpu_usage'] = psutil.cpu_percent(interval=1)
                real_time_stats['memory_usage'] = psutil.virtual_memory().percent
            else:
                # Fallback values
                real_time_stats['cpu_usage'] = 15.0  # Mock value
                real_time_stats['memory_usage'] = 45.0  # Mock value
            time.sleep(2)
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
            time.sleep(5)

# Start background stats monitoring
stats_thread = threading.Thread(target=update_system_stats, daemon=True)
stats_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/system-info')
def get_system_info():
    """Get system information for dashboard"""
    try:
        if PSUTIL_AVAILABLE:
            return jsonify({
                'python_version': sys.version.split()[0],
                'platform': sys.platform,
                'cpu_count': psutil.cpu_count(),
                'memory_total': round(psutil.virtual_memory().total / (1024**3), 2),  # GB
                'memory_available': round(psutil.virtual_memory().available / (1024**3), 2),  # GB
                'disk_usage': round(psutil.disk_usage('/').percent, 1) if sys.platform != 'win32' else round(psutil.disk_usage('C:\\').percent, 1),
                'uptime': time.time() - psutil.boot_time()
            })
        else:
            return jsonify({
                'python_version': sys.version.split()[0],
                'platform': sys.platform,
                'cpu_count': 4,  # Mock value
                'memory_total': 8.0,  # Mock value
                'memory_available': 4.5,  # Mock value
                'disk_usage': 65.0,  # Mock value
                'uptime': 3600  # Mock value
            })
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return jsonify({'error': 'Could not retrieve system information'})

@app.route('/api/real-time-stats')
def get_real_time_stats():
    """Get real-time compilation statistics and system metrics"""
    try:
        system_stats = {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'memory_used_gb': round(psutil.virtual_memory().used / (1024**3), 2),
            'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'disk_percent': psutil.disk_usage('C:\\' if sys.platform == 'win32' else '/').percent,
            'timestamp': datetime.now().isoformat()
        }
        
        # Merge with compilation stats
        combined_stats = {**real_time_stats, **system_stats}
        return jsonify(combined_stats)
        
    except Exception as e:
        logger.error(f"Real-time stats error: {e}")
        return jsonify(real_time_stats)  # Fallback to basic stats

@app.route('/api/code-analysis', methods=['POST'])
def analyze_code():
    """Analyze C code and provide insights"""
    try:
        data = request.json
        code = data.get('code', '')
        
        analysis = {
            'lines_of_code': len([line for line in code.split('\n') if line.strip()]),
            'functions': len([line for line in code.split('\n') if 'int ' in line and '(' in line and ')' in line]),
            'includes': len([line for line in code.split('\n') if line.strip().startswith('#include')]),
            'complexity_score': calculate_complexity(code),
            'suggestions': generate_detailed_suggestions(code),
            'security_issues': check_security_issues(code),
            'performance_tips': get_performance_tips(code)
        }
        
        return jsonify({'success': True, 'analysis': analysis})
        
    except Exception as e:
        logger.error(f"Code analysis error: {e}")
        return jsonify({'success': False, 'error': str(e)})

def calculate_complexity(code):
    """Calculate code complexity score"""
    score = 0
    keywords = ['if', 'for', 'while', 'switch', 'case']
    
    for keyword in keywords:
        score += code.count(keyword)
    
    # Normalize to 1-10 scale
    return min(10, max(1, score))

def generate_detailed_suggestions(code):
    """Generate detailed code suggestions"""
    suggestions = []
    
    # Check for common issues
    if 'printf' in code and '#include <stdio.h>' not in code:
        suggestions.append({
            'type': 'warning',
            'message': "Missing #include <stdio.h> for printf function",
            'line': 1,
            'severity': 'high'
        })
    
    if 'malloc' in code and 'free' not in code:
        suggestions.append({
            'type': 'warning',
            'message': "Memory allocated with malloc should be freed",
            'severity': 'medium'
        })
    
    if code.count('int main') > 1:
        suggestions.append({
            'type': 'error',
            'message': "Multiple main functions detected",
            'severity': 'high'
        })
    
    return suggestions

def check_security_issues(code):
    """Check for potential security issues"""
    issues = []
    
    if 'gets(' in code:
        issues.append({
            'type': 'security',
            'message': "gets() is unsafe, use fgets() instead",
            'severity': 'critical'
        })
    
    if 'strcpy(' in code:
        issues.append({
            'type': 'security',
            'message': "strcpy() can cause buffer overflow, consider strncpy()",
            'severity': 'medium'
        })
    
    return issues

def get_performance_tips(code):
    """Get performance optimization tips"""
    tips = []
    
    if 'int i' in code and 'for' in code:
        tips.append("Consider loop unrolling for better performance")
    
    if code.count('malloc') > 3:
        tips.append("Consider memory pooling for frequent allocations")
    
    if 'printf' in code and 'for' in code:
        tips.append("Minimize I/O operations inside loops")
    
    return tips

@app.route('/api/save-project', methods=['POST'])
def save_project():
    """Save current project to server"""
    try:
        data = request.json
        project_name = data.get('name', f'project_{int(time.time())}')
        code = data.get('code', '')
        config = data.get('config', {})
        
        # Create projects directory if it doesn't exist
        projects_dir = Path('saved_projects')
        projects_dir.mkdir(exist_ok=True)
        
        # Save project
        project_data = {
            'name': project_name,
            'code': code,
            'config': config,
            'created_at': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat()
        }
        
        project_file = projects_dir / f'{project_name}.json'
        with open(project_file, 'w') as f:
            json.dump(project_data, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'Project "{project_name}" saved successfully',
            'project_id': project_name
        })
        
    except Exception as e:
        logger.error(f"Error saving project: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/load-project/<project_id>')
def load_project(project_id):
    """Load a saved project"""
    try:
        project_file = Path('saved_projects') / f'{project_id}.json'
        
        if not project_file.exists():
            return jsonify({'success': False, 'error': 'Project not found'})
        
        with open(project_file, 'r') as f:
            project_data = json.load(f)
        
        return jsonify({'success': True, 'project': project_data})
        
    except Exception as e:
        logger.error(f"Error loading project: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/projects')
def list_projects():
    """List all saved projects"""
    try:
        projects_dir = Path('saved_projects')
        if not projects_dir.exists():
            return jsonify({'projects': []})
        
        projects = []
        for project_file in projects_dir.glob('*.json'):
            try:
                with open(project_file, 'r') as f:
                    project_data = json.load(f)
                    projects.append({
                        'id': project_file.stem,
                        'name': project_data.get('name', project_file.stem),
                        'created_at': project_data.get('created_at'),
                        'last_modified': project_data.get('last_modified')
                    })
            except Exception as e:
                logger.error(f"Error reading project {project_file}: {e}")
        
        # Sort by last modified
        projects.sort(key=lambda x: x.get('last_modified', ''), reverse=True)
        
        return jsonify({'projects': projects})
        
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        return jsonify({'projects': []})

@app.route('/api/generate-ir', methods=['POST'])
def generate_ir():
    """Generate LLVM IR for the given C code"""
    try:
        data = request.json
        code = data.get('code', '')
        
        if not code.strip():
            return jsonify({'success': False, 'error': 'No code provided'})
        
        # Generate IR using the compiler
        ir_code = compiler.generate_ir_only(code)
        
        return jsonify({
            'success': True,
            'ir_code': ir_code,
            'line_count': len(ir_code.split('\n'))
        })
        
    except Exception as e:
        logger.error(f"IR generation error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/download-binary', methods=['POST'])
def download_binary():
    """Compile and provide binary for download"""
    try:
        data = request.json
        code = data.get('code', '')
        
        if not code.strip():
            return jsonify({'success': False, 'error': 'No code provided'})
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(code)
            source_file = f.name
        
        # Compile to binary
        binary_file = source_file.replace('.c', '.exe' if sys.platform == 'win32' else '')
        
        try:
            # Use the compiler to generate binary
            compiler.compile_to_binary(code, binary_file)
            
            return send_file(binary_file, as_attachment=True, 
                           download_name='compiled_program.exe' if sys.platform == 'win32' else 'compiled_program')
        
        finally:
            # Cleanup
            try:
                os.unlink(source_file)
                if os.path.exists(binary_file):
                    # Don't delete binary immediately, let Flask handle it
                    pass
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
        
    except Exception as e:
        logger.error(f"Binary generation error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/compile', methods=['POST'])
def compile_code():
    """Main compilation endpoint with enhanced features"""
    try:
        data = request.json
        code = data.get('code', '')
        config = data.get('config', {})
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not code.strip():
            return jsonify({'success': False, 'error': 'No code provided'})
        
        # Update compiler configuration
        compiler.config.update(config)
        
        # Track compilation start
        start_time = time.time()
        real_time_stats['total_compilations'] = real_time_stats.get('total_compilations', 0) + 1
        real_time_stats['active_sessions'] = real_time_stats.get('active_sessions', 0) + 1
        
        # Store session info
        active_sessions[session_id] = {
            'start_time': start_time,
            'code_length': len(code),
            'config': config
        }
          # Compile and execute the code
        compilation_result = compiler.compile_and_execute(code)
        
        # Calculate compilation time
        compile_time = time.time() - start_time
        
        # Update stats
        real_time_stats['last_compile_time'] = compile_time
        real_time_stats['average_compile_time'] = real_time_stats.get('average_compile_time', compile_time)
        real_time_stats['active_sessions'] = real_time_stats.get('active_sessions', 1) - 1
        
        # Store in compilation history
        compilation_entry = {
            'id': session_id,
            'timestamp': datetime.now().isoformat(),
            'code_length': len(code),
            'compile_time': compile_time,
            'success': compilation_result['success'],
            'config': config
        }
        compilation_history.append(compilation_entry)
        
        # Keep only last 100 entries
        if len(compilation_history) > 100:
            compilation_history.pop(0)
        
        # Clean up session
        if session_id in active_sessions:
            del active_sessions[session_id]
        
        if compilation_result['success']:
            return jsonify({
                'success': True, 
                'result': compilation_result['output'],  # Return actual program output
                'compile_time': compile_time,
                'session_id': session_id,
                'message': compilation_result['message'],
                'ir_code': compilation_result.get('ir_code', ''),  # Include IR for advanced users
                'source_lines': compilation_result.get('source_lines', 0)
            })
        else:
            return jsonify({
                'success': False,
                'error': compilation_result['error'],
                'message': compilation_result['message'],
                'session_id': session_id
            })
        
    except Exception as e:
        logger.error(f"Compilation error: {str(e)}")
        
        # Update error stats
        real_time_stats['total_errors'] = real_time_stats.get('total_errors', 0) + 1
        real_time_stats['active_sessions'] = real_time_stats.get('active_sessions', 1) - 1
        
        # Clean up session on error
        if 'session_id' in locals() and session_id in active_sessions:
            del active_sessions[session_id]
        
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/compilation-history')
def get_compilation_history():
    """Get compilation history"""
    return jsonify({
        'success': True,
        'history': compilation_history[-20:]  # Return last 20 entries
    })

@app.route('/api/active-sessions')
def get_active_sessions():
    """Get currently active compilation sessions"""
    return jsonify({
        'success': True,
        'sessions': active_sessions,
        'count': len(active_sessions)
    })

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """Clear compilation history"""
    global compilation_history
    compilation_history = []
    return jsonify({'success': True, 'message': 'History cleared'})

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'uptime': time.time() - start_time if 'start_time' in globals() else 0
    })

if __name__ == '__main__':
    # Start background monitoring
    monitor_thread = threading.Thread(target=update_system_stats, daemon=True)
    monitor_thread.start()
    
    print("🚀 Starting AI-Powered C Compiler Web Interface...")
    print("📡 Server will be available at: http://localhost:5000")
    print("🤖 AI features: Enabled")
    print("⚡ Real-time monitoring: Active")
    print("🎯 Ready to compile C code!")
    
    # Start Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )