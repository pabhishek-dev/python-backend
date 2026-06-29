import requests
from simpleeval import simple_eval

# --- Configuration ---
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gemma4:e2b"  

SYSTEM_PROMPT = """You are an autonomous agent. You solve tasks step-by-step using tools.

Available Tools:
- calculator: Evaluates mathematical expressions.
- task_complete: Use this to provide your final answer to the user.

Format Requirements (use EXACTLY this format, nothing else):
TOOL: [tool_name]
INPUT: [tool_input]

IMPORTANT: You must always respond with a tool call. Never just talk. When you have the final answer, use task_complete."""


def chat(messages: list) -> str:
    """Sends the conversation history to Ollama and returns the text response."""
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.1} # Low temperature for more deterministic, logical outputs
        })
        data = response.json()
        return data.get("message", {}).get("content", "Error: No content returned.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Ensure it is running (ollama serve).")
        exit(1)


def parse_tool_call(text: str):
    """Extracts the requested tool and input from the model's text."""
    tool_name, tool_input = None, None
    
    for line in text.strip().split("\n"):
        if line.startswith("TOOL:"):
            tool_name = line.replace("TOOL:", "").strip().lower()
        if line.startswith("INPUT:"):
            tool_input = line.replace("INPUT:", "").strip()
            
    return tool_name, tool_input


def run_tool(name: str, tool_input: str) -> str:
    """Executes the tool safely and returns the result as a string."""
    if name == "calculator":
        try:
            # 🔒 simple_eval safely handles math and strictly blocks malicious python code
            result = simple_eval(tool_input)
            return str(result)
        except Exception as e:
            return f"Math Error: {e}"
            
    return f"Error: Tool '{name}' does not exist."


def run_agent(task: str, max_loops: int = 10) -> str:
    """The main ReAct loop that orchestrates the agent."""
    print(f"\n{'='*50}\n🎯 Goal: {task}\n{'='*50}")

    # The agent's memory
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task}
    ]

    for loop in range(1, max_loops + 1):
        print(f"\n🧠 [Thought Loop {loop}]")
        
        reply = chat(messages)
        tool_name, tool_input = parse_tool_call(reply)

        # 1. Check if task is complete
        if tool_name == "task_complete":
            print(f"✅ Finished! Final Answer:\n{tool_input}")
            return tool_input

        # 2. Check if a tool was called
        if tool_name:
            print(f"  🔧 Action: Using '{tool_name}' with input -> {tool_input}")
            result = run_tool(tool_name, tool_input)
            print(f"  ➡️  Observation: {result}")

            # Save the exchange to memory so the AI can read the result
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content": f"Tool observation: {result}\nContinue solving. Use task_complete when finished."})
            
        # 3. Handle formatting failures
        else:
            print(f"⚠️ Model forgot to use a tool. It said: {reply}")
            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content": "Error: You did not use the strict TOOL/INPUT format. Please try again."})

    print("\n🛑 Hit maximum loop limit. Stopping to prevent infinite loops.")
    return "Failed to complete task."


# --- Run it! ---
if __name__ == "__main__":
    # Try different tasks:
    # answer = run_agent("What is 47 * 89, then add 123 to the result?")
    # answer = run_agent("Calculate the area of a circle with radius 15.")
    answer = run_agent("If I have 2500 rupees and spend 37% on food, how much is left?")

    print(f"\nFinal answer: {answer}")