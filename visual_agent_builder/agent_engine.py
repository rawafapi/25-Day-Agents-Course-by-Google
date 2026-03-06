import os
from typing import List, Dict, Any

from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import ToolContext

# Pre-defined tools for the Visual Builder
def search_tool(query: str) -> str:
    """Simulates searching the web.
    
    Args:
        query: The search query string.
    """
    return f"Simulated search results for: {query}. (Found lots of relevant data)."

def calculator_tool(expression: str) -> str:
    """Evaluates a mathematical expression.
    
    Args:
        expression: The math expression to evaluate (e.g., '2 + 2').
    """
    try:
        # DO NOT use eval in production securely without sandbox, but this is a demo
        result = eval(expression)
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {e}"

AVAILABLE_TOOLS = {
    "search": search_tool,
    "calculator": calculator_tool
}

def execute_flow(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], initial_prompt: str) -> str:
    """Compiles the nodes and edges into ADK Agents and executes them."""
    
    if not nodes:
        return "Error: No agents defined in the visual flow."
        
    print(f"Engine starting execution with {len(nodes)} agents...")
    
    # 1. Parse Nodes into google.adk Agents
    adk_agents = {}
    
    for node in nodes:
        node_id = node.get("id")
        data = node.get("data", {})
        
        agent_name = data.get("name", f"Agent_{node_id}")
        instruction = data.get("instruction", "You are a helpful assistant.")
        model_name = data.get("model", "gemini-2.5-flash")
        selected_tools_names = data.get("tools", [])
        
        # Hydrate tool functions
        tools = [AVAILABLE_TOOLS[t] for t in selected_tools_names if t in AVAILABLE_TOOLS]
        
        # Instantiate the ADK Agent
        adk_agent = Agent(
            name=agent_name,
            model=model_name,
            instruction=instruction,
            tools=tools
        )
        adk_agents[node_id] = adk_agent
        print(f"Created Agent: {agent_name} with tools: {selected_tools_names}")
    
    # 2. Build Execution Sequence (Orchestrator)
    # To keep it simple, we sort edges to find the chain, or just execute all agents sequentially
    # Real visual builders would do topological sorting.
    # We will assume a simple a -> b -> c chain defined by edges, or just execute them in order of creation if no edges.
    
    ordered_agents = []
    
    if not edges:
        # Fallback: Just sequential order of nodes
        ordered_agents = list(adk_agents.values())
    else:
        # Very basic topological sort for a linear sequence
        # Find start node (has no incoming edges)
        incoming = {e["target"] for e in edges}
        current_node_id = next((n["id"] for n in nodes if n["id"] not in incoming), None)
        
        if not current_node_id:
            current_node_id = nodes[0]["id"] # Fallback if cycle
            
        edge_map = {e["source"]: e["target"] for e in edges}
        
        while current_node_id:
            ordered_agents.append(adk_agents[current_node_id])
            current_node_id = edge_map.get(current_node_id)
            if current_node_id and current_node_id not in adk_agents:
                break
    
    if len(ordered_agents) > 1:
        # Use SequentialAgent for multi-agent chains
        orchestrator = SequentialAgent(
            name="Visual_Flow_Orchestrator",
            sub_agents=ordered_agents
        )
        
        # Execute Pipeline
        try:
           # We simulate invoking it. In ADK, it runs sequentially passing context
            print(f"Invoking {orchestrator.name} with prompt: {initial_prompt}")
            response = orchestrator(initial_prompt)
            # In a real scenario, this returns raw objects, we mock the string response.
            return f"{response}"
        except Exception as e:
            return f"Pipeline Execution Error: {e}"
    else:
        # Single Agent Run
        agent = ordered_agents[0]
        try:
             print(f"Invoking Single Agent {agent.name}")
             response = agent(initial_prompt)
             return f"{response}"
        except Exception as e:
             return f"Agent Execution Error: {e}"

