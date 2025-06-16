import pytest
import os
from pathlib import Path

@pytest.fixture(scope="session")
def test_config_path(tmp_path_factory) -> Path:
    """Create a test configuration file."""
    config_path = tmp_path_factory.mktemp("config") / "test_config.yaml"
    
    config_content = """
    core:
      version: "1.0.0"
      debug: true
      logging:
        level: "DEBUG"
        format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        file: "test.log"
    
    compilation:
      optimization_level: 0
      target_arch: "x86_64"
      target_os: "linux"
      include_paths: []
      macros: {}
    
    ai:
      enabled: false
      model: "gpt-4"
      features:
        code_completion: false
        code_analysis: false
        optimization: false
        pattern_recognition: false
      analysis:
        complexity_threshold: 10
        performance_metrics: false
        security_checks: false
      optimization:
        level: "conservative"
        target: "performance"
    
    plugins:
      enabled: []
      disabled: []
      custom_paths: []
    
    web:
      host: "127.0.0.1"
      port: 5000
      debug: true
      secret_key: "test-secret-key"
      allowed_origins: ["http://localhost:5000"]
    """
    
    with open(config_path, "w") as f:
        f.write(config_content)
        
    return config_path
    
@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up the test environment."""
    # Set test environment variables
    os.environ["FLASK_ENV"] = "testing"
    os.environ["FLASK_APP"] = "compiler.web:create_app"
    
    yield
    
    # Clean up
    if "FLASK_ENV" in os.environ:
        del os.environ["FLASK_ENV"]
    if "FLASK_APP" in os.environ:
        del os.environ["FLASK_APP"] 