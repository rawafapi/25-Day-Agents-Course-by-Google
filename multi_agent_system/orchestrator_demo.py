import os
import argparse
from typing import Dict, Any

from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import ToolContext

# --- Simulated Tools ---
def search_web(query: str) -> str:
    """Simulates searching the web for information.
    
    Args:
        query: The search query string.
    """
    print(f"🔍 [Tool Execution] Searching Web for: {query}")
    if "quantum" in query.lower():
        return "Quantum computing uses qubits to perform calculations exponentially faster than classical computers for certain tasks. Key players include Google, IBM, and Microsoft."
    elif "ai" in query.lower():
        return "Artificial Intelligence refers to the simulation of human intelligence in machines. Recent advancements are largely driven by Large Language Models (LLMs)."
    return "Found a bunch of general results. The topic is very broad."

# --- Defining Agents ---
planner_agent = Agent(
    name="Planner",
    model="gemini-2.0-flash",
    instruction="""You are an expert Project Manager and Planner.
Your job is to take a user's broad request and break it down into a clear, actionable list of research steps and writing goals.
Output a structured plan with specific search queries needed, and instructions for the writer.
Do NOT do the research yourself.""",
)

researcher_agent = Agent(
    name="Researcher",
    model="gemini-2.0-flash",
    instruction="""You are a diligent Researcher.
Read the plan provided by the Planner. You MUST use the `search_web` tool to gather the information requested in the plan.
Synthesize all your findings into a comprehensive research document.
Ensure you cover all points requested by the planner.""",
    tools=[search_web],
)

writer_agent = Agent(
    name="Writer",
    model="gemini-2.0-flash",
    instruction="""You are a professional Technical Writer.
Take the synthesized research document provided by the Researcher and write a highly polished, engaging, and clear final report.
Use markdown formatting, including headers, bullet points, and bold text for emphasis.
Do not invent facts; only use the information given by the Researcher.""",
)

# --- Orchestrating the Flow ---
# We use SequentialAgent (similar to day-25) to automatically route Output of A -> Input of B
multi_agent_pipeline = SequentialAgent(
    name="Planner_Researcher_Writer_Orchestrator",
    description="A multi-agent flow that plans, researches, and writes a comprehensive report.",
    sub_agents=[
        planner_agent,    # Part 1: Break down the request
        researcher_agent, # Part 2: Execute search tools based on the plan
        writer_agent,     # Part 3: Write the final report
    ],
)

def run_orchestrator(topic: str):
    """Executes the pipeline on a given topic."""
    print(f"🚀 Starting Multi-Agent Pipeline for topic: '{topic}'")
    
    # We pass the initial request to the pipeline.
    # The SequentialAgent handles passing the outputs down the chain.
    try:
        # In Google ADK, agents are invoked via `__call__` or `run` usually.
        # Often SequentialAgent takes the input and automatically chains it.
        response = multi_agent_pipeline(f"Please create a comprehensive report on: {topic}. Give it to me in Markdown.")
        
        print("\n" + "="*50)
        print("✅ FINAL PIPELINE OUTPUT:")
        print("="*50)
        print(response)
        
    except Exception as e:
        print(f"❌ Error during pipeline execution: {e}")

if __name__ == "__main__":
    # Ensure API Key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️ Warning: GOOGLE_API_KEY environment variable not set. Please set it to run the agents.")
        # Alternatively, import from the shared config of the course
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from shared import get_api_key
            os.environ["GOOGLE_API_KEY"] = get_api_key()
            print("✅ Retrieved GOOGLE_API_KEY from .env")
        except:
            pass

    parser = argparse.ArgumentParser(description="Run the multi-agent orchestrator.")
    parser.add_argument("--topic", type=str, default="The future of Quantum Computing and AI", help="Topic to research and write about.")
    args = parser.parse_args()
    
    run_orchestrator(args.topic)
