import sys
import os
import json
from typing import Dict, Any
from crewai import Agent, Task, Crew, Process, LLM  # <--- Added native LLM class import

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from goal_manager import SavingsPlanSchema
from feasibility import calculate_base_feasibility
from crewai.tools import tool 

@tool("Financial Planning Knowledge Base")
def search_financial_knowledge(query: str) -> str:
    """Reads and returns the rules, budgeting frameworks, and priorities from the local knowledge base directory."""
    knowledge_path = "C:/Users/lenovo/FinplotAI/agent3/knowledge/goal_planning_principles.txt"
    try:
        if os.path.exists(knowledge_path):
            with open(knowledge_path, "r", encoding="utf-8") as file:
                return file.read()
        return "Standard framework guidance: 50/30/20 allocation rules apply. Build an emergency fund before secondary goals."
    except Exception as e:
        return f"Error reading local knowledge base files: {str(e)}"

def run_agent3_pipeline(agent1_json: Dict[str, Any], agent2_json: Dict[str, Any], user_goal_json: Dict[str, Any]) -> str:
    math_metrics = calculate_base_feasibility(agent1_json, user_goal_json)
    
    context_payload = {
        "financial_profile": agent1_json,
        "health_assessment": agent2_json,
        "user_intent": user_goal_json,
        "feasibility_math_metrics": math_metrics
    }
    
    # 1. Instantiate the native CrewAI LLM manager configuration.
    # This embeds resilient exponential retry logic deep inside the connection pool.
    resilient_cloud_llm = LLM(
        model="gemini/gemini-3.1-flash-lite",
        api_key=os.environ.get("GEMINI_API_KEY"),
        max_retries=5,       # Automatically absorbs spikes up to 5 times natively
        timeout=30           # Allows extra runway if the cloud servers are sluggish
    )
    
    # 2. Bind the custom LLM directly to your specialist agent object
    savings_specialist = Agent(
        role="Savings & Goal Planning Specialist",
        goal="Create a realistic, personalized savings strategy that helps the user achieve financial goals without causing unnecessary financial stress.",
        backstory=(
            "You are an expert personal financial strategist certified in consumer finance frameworks. "
            "Instead of relying on generic advice, you cross-reference explicit mathematical shortfalls "
            "against the professional financial planning guidelines injected into your context payload."
        ),
        tools=[search_financial_knowledge],
        llm=resilient_cloud_llm,  # <--- Bound the resilient endpoint config here
        verbose=True,
        allow_delegation=False,
        max_iter=3
    )
    
    formulate_strategy_task = Task(
        description=(
            f"Analyze the incoming personal financial profile context metrics:\n{json.dumps(context_payload, indent=2)}\n\n"
            "Execution Steps:\n"
            "1. Process target goal constraints vs current disposable bounds using the provided mathematical feasibility metrics.\n"
            "2. Query your knowledge tools to find the proper rules regarding emergency funds, lifestyle prioritization, and timeline extension strategies.\n"
            "3. If math metrics show the goal is NOT feasible, use the retrieved rules to reason out an optimized adjustment.\n"
            "4. Structure a comprehensive, optimized month-by-month timeline blueprint."
        ),
        expected_output="Structured optimization strategy schema containing allocations, reductions, and feasibility validations.",
        agent=savings_specialist,
        output_json=SavingsPlanSchema
    )
    
    crew_orchestrator = Crew(
        agents=[savings_specialist],
        tasks=[formulate_strategy_task],
        process=Process.sequential
    )
    
    # Execution block now relies safely on the native retry handler
    output_result = crew_orchestrator.kickoff()
    return output_result