import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from compiler.ai import AIAnalyzer
from compiler.config import ConfigLoader
from compiler.exceptions import CompilerError

@pytest.fixture
def ai_config() -> ConfigLoader:
    """Create a test configuration with AI enabled."""
    config = ConfigLoader()
    config.set("ai.enabled", True)
    config.set("ai.api_key", "test-api-key")
    config.set("ai.features.code_analysis", True)
    config.set("ai.features.optimization", True)
    return config
    
@pytest.fixture
def ai_analyzer(ai_config: ConfigLoader) -> AIAnalyzer:
    """Create a test AI analyzer."""
    return AIAnalyzer(ai_config)
    
def test_ai_analyzer_init(ai_config: ConfigLoader):
    """Test AI analyzer initialization."""
    analyzer = AIAnalyzer(ai_config)
    assert analyzer.config == ai_config
    assert analyzer.model == "gpt-4"
    assert analyzer.features["code_analysis"]
    
def test_ai_analyzer_init_no_api_key():
    """Test AI analyzer initialization without API key."""
    config = ConfigLoader()
    config.set("ai.enabled", True)
    with pytest.raises(CompilerError):
        AIAnalyzer(config)
        
@patch("openai.ChatCompletion.create")
def test_analyze_success(mock_create: MagicMock, ai_analyzer: AIAnalyzer):
    """Test successful code analysis."""
    mock_create.return_value.choices = [MagicMock(message=MagicMock(content="""
    {
        "complexity": 5,
        "security_issues": [],
        "suggestions": ["Use more descriptive variable names"],
        "performance_metrics": {
            "memory_usage": 3,
            "execution_time": 2,
            "optimization_potential": 4
        }
    }
    """))]
    
    result = ai_analyzer.analyze(None, "int main() { return 0; }")
    assert result["success"]
    assert "suggestions" in result
    assert result["complexity"] == 5
    
@patch("openai.ChatCompletion.create")
def test_analyze_failure(mock_create: MagicMock, ai_analyzer: AIAnalyzer):
    """Test code analysis failure."""
    mock_create.side_effect = Exception("API Error")
    
    result = ai_analyzer.analyze(None, "int main() { return 0; }")
    assert not result["success"]
    assert "error" in result
    
@patch("openai.ChatCompletion.create")
def test_optimize_success(mock_create: MagicMock, ai_analyzer: AIAnalyzer):
    """Test successful code optimization."""
    mock_create.return_value.choices = [MagicMock(message=MagicMock(content="""
    [
        {
            "type": "loop_unrolling",
            "location": "10",
            "improvement": "Reduced loop overhead",
            "code": "// Optimized code"
        }
    ]
    """))]
    
    result = ai_analyzer.optimize("test ir module")
    assert result == "test ir module"  # Placeholder implementation
    
@patch("openai.ChatCompletion.create")
def test_optimize_failure(mock_create: MagicMock, ai_analyzer: AIAnalyzer):
    """Test code optimization failure."""
    mock_create.side_effect = Exception("API Error")
    
    result = ai_analyzer.optimize("test ir module")
    assert result == "test ir module"  # Should return original module on failure
    
def test_ai_disabled(ai_config: ConfigLoader):
    """Test behavior when AI is disabled."""
    ai_config.set("ai.enabled", False)
    analyzer = AIAnalyzer(ai_config)
    
    # Analysis should return empty result
    result = analyzer.analyze(None, "int main() { return 0; }")
    assert result == {}
    
    # Optimization should return original module
    result = analyzer.optimize("test ir module")
    assert result == "test ir module" 