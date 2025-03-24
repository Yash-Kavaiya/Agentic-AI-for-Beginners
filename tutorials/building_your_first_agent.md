# 🚀 Building Your First Agentic AI

> *A step-by-step guide to creating a simple but powerful AI agent*

## 📋 Table of Contents

- [Introduction](#-introduction)
- [Prerequisites](#-prerequisites)
- [Project Structure](#-project-structure)
- [Step 1: Setting Up Your Environment](#-step-1-setting-up-your-environment)
- [Step 2: Creating the Agent Class](#-step-2-creating-the-agent-class)
- [Step 3: Implementing Core Components](#-step-3-implementing-core-components)
- [Step 4: Adding Tools](#-step-4-adding-tools)
- [Step 5: Running Your Agent](#-step-5-running-your-agent)
- [Next Steps](#-next-steps)

## 🌟 Introduction

In this tutorial, we'll build a simple yet functional AI agent that can:

1. Understand user requests
2. Break down tasks into steps
3. Use tools to complete those tasks
4. Provide helpful responses

Our agent will use a Large Language Model (LLM) as its brain and implement a basic version of the ReAct (Reasoning + Acting) pattern.

## 🧰 Prerequisites

Before we begin, make sure you have:

- Python 3.8+ installed
- Basic knowledge of Python programming
- An API key for an LLM service (we'll use OpenAI's GPT in this example)
- Basic understanding of APIs and JSON

## 📂 Project Structure

```
my_first_agent/
│
├── agent.py         # Main agent implementation
├── tools.py         # Tool implementations
├── memory.py        # Simple memory system
├── config.py        # Configuration settings
└── run.py           # Script to run the agent
```

## 🔧 Step 1: Setting Up Your Environment

First, let's create a virtual environment and install the necessary packages:

```bash
# Create a new directory for your project
mkdir my_first_agent
cd my_first_agent

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install requests openai python-dotenv
```

Create a `.env` file to store your API key securely:

```
OPENAI_API_KEY=your_api_key_here
```

Now, let's create a `config.py` file:

```python
# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-3.5-turbo"  # or another model you prefer

# Agent settings
AGENT_NAME = "MyFirstAgent"
AGENT_DESCRIPTION = "A helpful AI assistant that can use tools to complete tasks."

# Tool settings
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")  # Optional
```

## 🧠 Step 2: Creating the Agent Class

Now, let's create the main agent implementation in `agent.py`:

```python
# agent.py
import json
import requests
from typing import List, Dict, Any, Optional

from config import OPENAI_API_KEY, MODEL_NAME
from tools import get_available_tools
from memory import Memory

class Agent:
    """A simple agentic AI that can understand tasks and use tools to complete them."""
    
    def __init__(self, name: str, description: str):
        """Initialize the agent with necessary configurations."""
        self.name = name
        self.description = description
        self.api_key = OPENAI_API_KEY
        self.model = MODEL_NAME
        
        # Initialize memory
        self.memory = Memory()
        
        # Initialize tools
        self.tools = get_available_tools()
    
    def chat(self, user_message: str) -> str:
        """Process a user message and return a response."""
        # Add user message to memory
        self.memory.add_user_message(user_message)
        
        # Process the message in steps
        task = self._understand_task(user_message)
        plan = self._create_plan(task)
        result = self._execute_plan(plan)
        response = self._generate_response(result)
        
        # Add agent response to memory
        self.memory.add_agent_message(response)
        
        return response
    
    def _understand_task(self, message: str) -> Dict[str, Any]:
        """Understand what the user is asking for."""
        prompt = f"""
        You are {self.name}, {self.description}
        
        Please analyze this user request and extract the main task:
        "{message}"
        
        Return a JSON object with:
        1. The main task or question
        2. Any relevant parameters or context
        3. The appropriate tool to use, if any (options: {', '.join(self.tools.keys())})
        """
        
        response = self._call_llm(prompt)
        
        try:
            # Parse the JSON response
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback if the response isn't valid JSON
            return {
                "task": message,
                "parameters": {},
                "tool": None
            }
    
    def _create_plan(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create a plan to complete the task."""
        prompt = f"""
        You are {self.name}, {self.description}
        
        Given this task: {json.dumps(task)}
        
        Create a step-by-step plan to complete it. You can use these tools: {', '.join(self.tools.keys())}
        
        Return a JSON array of steps, where each step has:
        1. A description of the step
        2. The tool to use (if any)
        3. The parameters for the tool
        """
        
        response = self._call_llm(prompt)
        
        try:
            # Parse the JSON response
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback if the response isn't valid JSON
            return [{
                "description": "Process the user's request",
                "tool": None,
                "parameters": {}
            }]
    
    def _execute_plan(self, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute the plan and collect results."""
        results = []
        
        for step in plan:
            step_result = {
                "step": step["description"],
                "output": None,
                "error": None
            }
            
            tool_name = step.get("tool")
            if tool_name and tool_name in self.tools:
                try:
                    # Call the tool with parameters
                    tool_fn = self.tools[tool_name]
                    parameters = step.get("parameters", {})
                    step_result["output"] = tool_fn(**parameters)
                except Exception as e:
                    step_result["error"] = str(e)
            
            results.append(step_result)
        
        return {"results": results}
    
    def _generate_response(self, execution_results: Dict[str, Any]) -> str:
        """Generate a helpful response based on the execution results."""
        # Get recent conversation history
        history = self.memory.get_recent_messages(5)
        
        prompt = f"""
        You are {self.name}, {self.description}
        
        Recent conversation:
        {json.dumps(history)}
        
        You've just completed this plan: {json.dumps(execution_results)}
        
        Please create a helpful, friendly response to the user based on these results.
        The response should be informative and directly address their query.
        """
        
        return self._call_llm(prompt)
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM API to get a response."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
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
```

## 🧠 Step 3: Implementing Core Components

Next, let's create a simple memory system in `memory.py`:

```python
# memory.py
from typing import List, Dict, Any
from datetime import datetime

class Memory:
    """A simple memory system for the agent."""
    
    def __init__(self, max_messages: int = 100):
        """Initialize the memory system."""
        self.messages = []
        self.max_messages = max_messages
    
    def add_user_message(self, message: str) -> None:
        """Add a user message to memory."""
        self._add_message("user", message)
    
    def add_agent_message(self, message: str) -> None:
        """Add an agent message to memory."""
        self._add_message("agent", message)
    
    def _add_message(self, role: str, content: str) -> None:
        """Add a message to memory with timestamp."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trim memory if it exceeds max size
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def get_recent_messages(self, count: int) -> List[Dict[str, Any]]:
        """Get the most recent messages."""
        return self.messages[-count:] if count < len(self.messages) else self.messages
    
    def get_all_messages(self) -> List[Dict[str, Any]]:
        """Get all messages in memory."""
        return self.messages
    
    def clear(self) -> None:
        """Clear all messages from memory."""
        self.messages = []
```

## 🛠️ Step 4: Adding Tools

Now, let's implement some tools for our agent in `tools.py`:

```python
# tools.py
import requests
import json
import math
from datetime import datetime
from typing import Dict, Any, Callable

from config import WEATHER_API_KEY

def search_wikipedia(query: str) -> Dict[str, Any]:
    """Search Wikipedia for information."""
    url = "https://en.wikipedia.org/w/api.php"
    
    # First, search for articles
    search_params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "utf8": 1
    }
    
    response = requests.get(url, params=search_params)
    data = response.json()
    
    if not data["query"]["search"]:
        return {"error": "No results found"}
    
    # Get the first result
    first_result = data["query"]["search"][0]
    page_id = first_result["pageid"]
    
    # Now get the summary
    summary_params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "exintro": 1,
        "explaintext": 1,
        "pageids": page_id
    }
    
    response = requests.get(url, params=summary_params)
    data = response.json()
    
    return {
        "title": first_result["title"],
        "summary": data["query"]["pages"][str(page_id)]["extract"],
        "url": f"https://en.wikipedia.org/?curid={page_id}"
    }

def get_weather(location: str) -> Dict[str, Any]:
    """Get current weather for a location."""
    if not WEATHER_API_KEY:
        # Return simulated data if no API key is available
        return {
            "location": location,
            "temperature": "22°C",
            "conditions": "Partly Cloudy",
            "humidity": "65%",
            "note": "This is simulated data as no weather API key was provided."
        }
    
    # Use a real weather API if key is available
    url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if response.status_code != 200:
        return {"error": f"Could not get weather: {data.get('message', 'Unknown error')}"}
    
    return {
        "location": f"{data['name']}, {data['sys']['country']}",
        "temperature": f"{data['main']['temp']}°C",
        "conditions": data['weather'][0]['description'],
        "humidity": f"{data['main']['humidity']}%",
        "wind": f"{data['wind']['speed']} m/s"
    }

def perform_calculation(expression: str) -> Dict[str, Any]:
    """Safely evaluate a mathematical expression."""
    # Clean and validate the expression
    allowed_chars = set("0123456789+-*/^() .")
    if not all(c in allowed_chars for c in expression):
        return {"error": "Invalid characters in expression"}
    
    # Replace ^ with ** for exponentiation
    expression = expression.replace("^", "**")
    
    try:
        # Use eval with only mathematical operations
        # This is still not completely safe, but better than raw eval
        result = eval(expression, {"__builtins__": {}}, {
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "sqrt": math.sqrt, "pi": math.pi, "e": math.e
        })
        return {"result": result}
    except Exception as e:
        return {"error": f"Error in calculation: {str(e)}"}

def get_date_time() -> Dict[str, Any]:
    """Get the current date and time."""
    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day": now.strftime("%A"),
        "month": now.strftime("%B"),
        "year": now.strftime("%Y"),
        "unix_timestamp": int(now.timestamp())
    }

def get_available_tools() -> Dict[str, Callable]:
    """Return a dictionary of all available tools."""
    return {
        "search_wikipedia": search_wikipedia,
        "get_weather": get_weather,
        "calculate": perform_calculation,
        "get_date_time": get_date_time
    }
```

## 🚀 Step 5: Running Your Agent

Finally, let's create a script to run our agent, `run.py`:

```python
# run.py
from agent import Agent
from config import AGENT_NAME, AGENT_DESCRIPTION

def main():
    """Run the agent in an interactive chat loop."""
    # Create the agent
    agent = Agent(AGENT_NAME, AGENT_DESCRIPTION)
    
    # Welcome message
    print(f"🤖 Welcome to {AGENT_NAME}!")
    print(f"🔍 {AGENT_DESCRIPTION}")
    print("💬 Type 'exit' to end the conversation.\n")
    
    # Chat loop
    while True:
        # Get user input
        user_input = input("You: ")
        
        # Check for exit command
        if user_input.lower() in ["exit", "quit", "bye"]:
            print(f"\n{AGENT_NAME}: Goodbye! Have a great day! 👋")
            break
        
        try:
            # Process user message
            response = agent.chat(user_input)
            print(f"\n{AGENT_NAME}: {response}\n")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")

if __name__ == "__main__":
    main()
```

## 🏃‍♂️ Running Your Agent

Now you can run your agent with:

```bash
python run.py
```

Try asking it questions like:
- "What's the weather like in New York?"
- "Can you calculate 354 * 89?"
- "Tell me about quantum computing"
- "What time is it now?"

## 🚀 Next Steps

Congratulations! You've built a simple but functional agentic AI system. Here are some ways to extend it:

1. **Improve the agent's memory**:
   - Implement vector-based memory for semantic search
   - Add long-term persistent storage

2. **Add more tools**:
   - Web browsing capability
   - Email sending functionality
   - Calendar integration

3. **Enhance the planning system**:
   - Implement hierarchical planning
   - Add plan verification steps

4. **Improve conversation**:
   - Add user preferences and personalization
   - Implement better error handling

5. **Add evaluation metrics**:
   - Track task completion success rate
   - Measure response quality

Remember, the best way to learn is to experiment and build. Keep iterating on your agent, and soon you'll be building complex autonomous systems!

---

⭐ **Continue your learning journey through our other tutorials** ⭐