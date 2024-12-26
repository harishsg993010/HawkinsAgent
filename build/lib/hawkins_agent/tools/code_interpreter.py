"""Code interpreter tool implementation using Open Interpreter"""

import os
from typing import Dict, Any
import logging
from interpreter import OpenInterpreter
from .base import BaseTool
from ..types import ToolResponse

logger = logging.getLogger(__name__)

class CodeInterpreterTool(BaseTool):
    """Tool for writing and running code based on problem descriptions"""

    def __init__(self, model: str = "gpt-4o", api_key: str = None, api_base: str = None):
        """Initialize the code interpreter tool
        
        Args:
            model: The model to use for code generation
            api_key: Optional OpenAI API key
            api_base: Optional OpenAI API base URL
        """
        super().__init__(name="code_interpreter")
        self.interpreter = OpenInterpreter()
        self.interpreter.llm.model = model
        self.interpreter.llm.api_key = (
            api_key if api_key else os.environ.get("OPENAI_API_KEY")
        )
        if api_base:
            self.interpreter.llm.api_base = api_base
        elif "OPENAI_BASE_URL" in os.environ:
            self.interpreter.llm.api_base = os.environ["OPENAI_BASE_URL"]

    @property
    def description(self) -> str:
        """Get the tool description"""
        return "Order a programmer to write and run code based on the description of a problem"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate the parameters
        
        Args:
            params: Parameters to validate
            
        Returns:
            True if parameters are valid
        """
        if 'query' not in params:
            logger.error("Missing required 'query' parameter")
            return False
            
        query = params.get('query')
        if not isinstance(query, str) or not query.strip():
            logger.error("Query must be a non-empty string")
            return False
            
        return True

    async def execute(self, **kwargs) -> ToolResponse:
        """Execute the code interpreter
        
        Args:
            **kwargs: Must include 'query' parameter
            
        Returns:
            ToolResponse containing the execution results
        """
        try:
            # Extract and validate query
            query = kwargs.get("query", "")
            if not self.validate_params({"query": query}):
                return ToolResponse(
                    success=False,
                    error="Invalid or missing query parameter",
                    result=None
                )

            logger.info(f"Executing code interpreter for query: {query}")
            
            # Run the interpreter
            messages = self.interpreter.chat(query, display=False)
            
            # Process results
            code = []
            console = []
            content = ""
            
            for message in messages:
                if message["type"] == "code":
                    code.append(message["content"])
                elif message["type"] == "console":
                    console.append(message["content"])
                elif message["type"] == "message":
                    content += message["content"] + "\n"

            result = {
                "messages": messages,
                "code": code,
                "console": console,
                "content": content.strip()
            }

            logger.info("Code interpreter execution completed successfully")
            return ToolResponse(
                success=True,
                result=result,
                error=None
            )

        except Exception as e:
            error_msg = f"Code interpreter execution failed: {str(e)}"
            logger.error(error_msg)
            return ToolResponse(
                success=False,
                result=None,
                error=error_msg
            )
