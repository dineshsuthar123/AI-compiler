import openai
from typing import Dict, Any, List, Optional

from compiler.config import ConfigLoader
from compiler.exceptions import CompilerError

class AIAnalyzer:
    """Handles AI-powered code analysis and optimization."""
    
    def __init__(self, config: ConfigLoader):
        """Initialize the AI analyzer."""
        self.config = config
        self.model = config.get("ai.model", "gpt-4")
        self.features = config.get("ai.features", {})
        self.analysis_config = config.get("ai.analysis", {})
        self.optimization_config = config.get("ai.optimization", {})
        
        # Initialize OpenAI client
        api_key = config.get("ai.api_key")
        if not api_key:
            raise CompilerError("OpenAI API key not configured")
        openai.api_key = api_key
        
    def analyze(self, ast: Any, source_code: str) -> Dict[str, Any]:
        """Analyze code using AI.
        
        Args:
            ast: The abstract syntax tree
            source_code: The original source code
            
        Returns:
            Dictionary containing analysis results
        """
        if not self.features.get("code_analysis", False):
            return {}
            
        try:
            # Prepare analysis prompt
            prompt = self._create_analysis_prompt(source_code)
            
            # Get AI response
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code analyzer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse response
            analysis = self._parse_analysis_response(response.choices[0].message.content)
            
            return {
                "success": True,
                "suggestions": analysis.get("suggestions", []),
                "complexity": analysis.get("complexity", 0),
                "security_issues": analysis.get("security_issues", []),
                "performance_metrics": analysis.get("performance_metrics", {})
            }
            
        except Exception as e:
            print(f"Warning: AI analysis failed: {e}")
            return {"success": False, "error": str(e)}
            
    def optimize(self, ir_module: Any) -> Any:
        """Optimize code using AI.
        
        Args:
            ir_module: The LLVM IR module to optimize
            
        Returns:
            The optimized IR module
        """
        if not self.features.get("optimization", False):
            return ir_module
            
        try:
            # Prepare optimization prompt
            prompt = self._create_optimization_prompt(str(ir_module))
            
            # Get AI response
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert code optimizer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse and apply optimizations
            optimizations = self._parse_optimization_response(response.choices[0].message.content)
            return self._apply_optimizations(ir_module, optimizations)
            
        except Exception as e:
            print(f"Warning: AI optimization failed: {e}")
            return ir_module
            
    def _create_analysis_prompt(self, source_code: str) -> str:
        """Create a prompt for code analysis."""
        prompt = f"""Analyze the following code and provide:
1. Code complexity score (1-10)
2. List of potential security issues
3. Performance optimization suggestions
4. Code style and best practices recommendations

Code:
{source_code}

Consider:
- Complexity threshold: {self.analysis_config.get('complexity_threshold', 10)}
- Performance metrics: {self.analysis_config.get('performance_metrics', True)}
- Security checks: {self.analysis_config.get('security_checks', True)}

Format your response as a JSON object with the following structure:
{{
    "complexity": <score>,
    "security_issues": ["issue1", "issue2", ...],
    "suggestions": ["suggestion1", "suggestion2", ...],
    "performance_metrics": {{
        "memory_usage": <score>,
        "execution_time": <score>,
        "optimization_potential": <score>
    }}
}}"""
        return prompt
        
    def _create_optimization_prompt(self, ir_code: str) -> str:
        """Create a prompt for code optimization."""
        prompt = f"""Optimize the following LLVM IR code for:
- Target: {self.optimization_config.get('target', 'performance')}
- Level: {self.optimization_config.get('level', 'moderate')}

Code:
{ir_code}

Provide a list of specific optimizations to apply, including:
1. The optimization type
2. The location in the code
3. The expected improvement

Format your response as a JSON array of optimization objects:
[
    {{
        "type": "<optimization_type>",
        "location": "<line_number>",
        "improvement": "<description>",
        "code": "<optimized_code>"
    }},
    ...
]"""
        return prompt
        
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI analysis response."""
        try:
            import json
            return json.loads(response)
        except json.JSONDecodeError:
            print("Warning: Failed to parse AI analysis response")
            return {}
            
    def _parse_optimization_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse the AI optimization response."""
        try:
            import json
            return json.loads(response)
        except json.JSONDecodeError:
            print("Warning: Failed to parse AI optimization response")
            return []
            
    def _apply_optimizations(self, ir_module: Any, optimizations: List[Dict[str, Any]]) -> Any:
        """Apply the suggested optimizations to the IR module."""
        # This is a placeholder - actual implementation would depend on the IR format
        # and the specific optimizations suggested
        return ir_module 