import os
import json
from typing import Dict, Any
from crewai import Agent, Task, Crew, Process, LLM

# Relative imports from your companion subfolders
from goal_manager.models import SavingsPlanSchema
from feasibility.engine import calculate_base_feasibility

# Core framework engine instantiation[cite: 5]
gemini_llm = LLM(
    model="gemini/gemini-2.5-flash",
    temperature=0.2
)

def run_agent3_pipeline(agent1_json: Dict[str, Any], agent2_json: Dict[str, Any], user_goal_json: Dict[str, Any]) -> str:
    """
    Orchestrates the complete flow: ingests data from previous agents, runs calculations, 
    and returns a structured strategy roadmap[cite: 5].
    """
    # Step 1: Execute local deterministic engine calculations[cite: 5]
    math_metrics = calculate_base_feasibility(agent1_json, user_goal_json)
    
    # Step 2: Assemble structured metadata for the LLM task[cite: 5]
    context_payload = {
        "financial_profile": agent1_json,
        "health_assessment": agent2_json,
        "user_intent": user_goal_json,
        "feasibility_math_metrics": math_metrics
    }
    
    # Step 3: Define the CrewAI planner specialist[cite: 5]
    savings_specialist = Agent(
        role="Savings & Goal Planning Specialist",
        goal="Create a realistic, personalized savings strategy that helps the user achieve financial goals without causing unnecessary financial stress[cite: 5].",
        backstory=(
            "You are an expert personal financial strategist[cite: 5]. Your core expertise lies in parsing structural "
            "spending habits, looking at downstream budgeting indicators, and restructuring variable outlays "
            "to help users consistently meet their goals[cite: 5]."
        ),
        llm=gemini_llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Step 4: Map operational instructions to the task execution block[cite: 5]
    formulate_strategy_task = Task(
        description=(
            f"Analyze the incoming personal financial profile context metrics:\n{json.dumps(context_payload, indent=2)}\n\n"
            "Execution Steps:\n"
            "1. Process target goal constraints vs current disposable bounds[cite: 5].\n"
            "2. Evaluate weaknesses from Agent 2 to extract strategic expense cutbacks (e.g. Shopping, Food Delivery)[cite: 5].\n"
            "3. If math metrics show 'mathematically_feasible' is false, recommend precise optimization actions to make it realistic[cite: 5].\n"
            "4. Structure a comprehensive, optimized month-by-month timeline blueprint[cite: 5]."
        ),
        expected_output="Structured optimization strategy schema containing allocations, reductions, and feasibility validations[cite: 5].",
        agent=savings_specialist,
        output_json=SavingsPlanSchema
    )
    
    # Step 5: Execute sequentially[cite: 5]
    crew_orchestrator = Crew(
        agents=[savings_specialist],
        tasks=[formulate_strategy_task],
        process=Process.sequential
    )
    
    output_result = crew_orchestrator.kickoff()
    return output_result