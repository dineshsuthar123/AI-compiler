from flask import Flask, render_template, request, jsonify
from simple_compiler import ModernCompiler
import logging

app = Flask(__name__)
compiler = ModernCompiler()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compile', methods=['POST'])
def compile_code():
    try:
        data = request.json
        code = data.get('code', '')
        config = data.get('config', {})
        
        # Update compiler configuration
        compiler.config.update(config)
        
        # Compile the code
        result = compiler.compile(code, execute=True)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        logging.error(f"Compilation error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True) 