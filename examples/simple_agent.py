"""
🤖 Simple Agentic AI Example
============================

This example demonstrates a basic agentic AI that can:
1. Parse user requests
2. Plan steps to complete the task
3. Execute those steps
4. Provide results back to the user

Requirements:
- Python 3.8+
- OpenAI API key
- requests library
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional

# Set your API key here or as an environment variable
# os.environ["OPENAI_API_KEY"] = "your-api-key"

class SimpleAgent:
    """A basic agentic AI that can process tasks and use tools."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the agent with necessary configurations."""
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.tools = {
            "search_web": self.search_web,
            "calculate": self.calculate,
            "get_weather": self.get_weather,
        }
        
        self.memory = []  # Simple memory to store conversation history
    
    def chat(self, message: str) -> str:
        """Process user message and return a response."""
        # Add user message to memory
        self.memory.append({"role": "user", "content": message})
        
        # 1. Parse the task
        task = self._parse_task(message)
        
        # 2. Plan steps
        steps = self._plan_steps(task)
        
        # 3. Execute steps
        result = self._execute_steps(steps)
        
        # 4. Generate response
        response = self._generate_response(result)
        
        # Add agent response to memory
        self.memory.append({"role": "assistant", "content": response})
        
        return response
    
    def _parse_task(self, message: str) -> Dict[str, Any]:
        """Parse the user message to understand the task."""
        prompt = f"""
        Parse the following user request into a structured task:
        
        User request: {message}
        
        Return a JSON object with the following structure:
        {{
            "task_type": "search" or "calculate" or "weather" or "general",
            "query": "the main query or question",
            "parameters": {{}} # any additional parameters
        }}
        """
        
        response = self._call_llm(prompt)
        return json.loads(response)
    
    def _plan_steps(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan the steps needed to complete the task."""
        prompt = f"""
        Given the following task, plan the steps needed to complete it:
        
        Task: {json.dumps(task)}
        
        Return a JSON array of step objects with the following structure:
        [
            {{
                "tool": "name of the tool to use",
                "parameters": {{}} # parameters for the tool
            }}
        ]
        """
        
        response = self._call_llm(prompt)
        return json.loads(response)
    
    def _execute_steps(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute the planned steps using available tools."""
        results = []
        
        for step in steps:
            tool_name = step["tool"]
            parameters = step["parameters"]
            
            if tool_name in self.tools:
                tool_result = self.tools[tool_name](**parameters)
                results.append({
                    "step": step,
                    "result": tool_result
                })
            else:
                results.append({
                    "step": step,
                    "error": f"Tool '{tool_name}' not found"
                })
        
        return {"results": results}
    
    def _generate_response(self, execution_results: Dict[str, Any]) -> str:
        """Generate a human-friendly response based on execution results."""
        prompt = f"""
        Given the following execution results, generate a helpful response for the user:
        
        Results: {json.dumps(execution_results)}
        
        Prior conversation:
        {json.dumps(self.memory[-10:])}
        """
        
        return self._call_llm(prompt)
    
    def _call_llm(self, prompt: str) -> str:
        """Call the language model to get a response."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"API call failed: {response.text}")
    
    # Tool implementations
    
    def search_web(self, query: str) -> Dict[str, Any]:
        """Simulate searching the web for information."""
        # In a real implementation, this would call a search API
        return {
            "result": f"Simulated search results for: {query}",
            "source": "web_search_simulation"
        }
    
    def calculate(self, expression: str) -> Dict[str, Any]:
        """Perform a calculation."""
        try:
            # CAUTION: eval is used here for simplicity
            # In production, use a safer alternative!
            result = eval(expression)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}
    
    def get_weather(self, location: str) -> Dict[str, Any]:
        """Simulate getting weather information."""
        # In a real implementation, this would call a weather API
        return {
            "location": location,
            "temperature": "72°F",
            "conditions": "Sunny",
            "source": "weather_simulation"
        }


# Example usage
if __name__ == "__main__":
    try:
        agent = SimpleAgent()
        
        print("🤖 Simple Agentic AI - Type 'exit' to quit")
        print("----------------------------------------")
        
        while True:
            user_input = input("\n👤 You: ")
            if user_input.lower() == "exit":
                print("\n🤖 Agent: Goodbye!")
                break
            
            response = agent.chat(user_input)
            print(f"\n🤖 Agent: {response}")
    
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
