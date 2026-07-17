import os
import json
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, Process, LLM

# Reference the local retrieval pipeline cleanly
from rag import retrieve_knowledge 

# --- STRUCTURAL OUTPUT SCHEMAS ---
class InvestmentOption(BaseModel):
    category_name: str = Field(..., description="Name of the investment category (e.g., PPF, Index Funds).")
    monthly_contribution: float = Field(..., description="Calculated monthly allocation amount.")
    security_level: str = Field(..., description="Security classification (e.g., Govt-Backed, Market-Linked).")
    risk_level: str = Field(..., description="Risk tier (Low, Medium, High).")
    simple_explanation: str = Field(..., description="Plain explanation of how it operates on a monthly basis.")
    important_features: List[str] = Field(..., description="Key features such as liquidity limits or lock-in terms.")

class InvestmentStrategySchema(BaseModel):
    risk_profile: str = Field(..., description="Assessed risk capability profile tier.")
    total_monthly_investment: float = Field(..., description="Total available funds routed for investments.")
    investment_options: List[InvestmentOption] = Field(..., description="List of 5-6 structured investment pathways generated.")
    best_recommended_option: str = Field(..., description="The definitive top-tier single selection chosen by the LLM logic.")
    reasoning_for_best_choice: str = Field(..., description="Contextual reason why this target option suits the profile.")
    disclaimer: str = Field(..., description="Standard educational compliance disclaimer note.")

# --- CORE PIPELINE PROCESSING TRACK ---
def run_agent4_pipeline(agent1_json: Dict[str, Any], agent2_json: Dict[str, Any], agent3_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ingests live parameters, executes a local RAG semantic search,
    and runs a validated Gemini configuration loop to build a strategy matrix.
    """
    # =========================================================================
    # CRITICAL AUTHENTICATION FIX:
    # Programmatically strip GOOGLE_API_KEY so LiteLLM is forced to use standard 
    # Google AI Studio API key headers instead of failing Vertex AI OAuth checks.
    # =========================================================================
    os.environ.pop("GOOGLE_API_KEY", None)
    os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
    os.environ.pop("VERTEXAI_API_KEY", None)

    # Fetch the correct API key parameter safely
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
         raise ValueError("Missing API key! Ensure GEMINI_API_KEY is set in your environment.")
    os.environ["OPENAI_API_KEY"] = api_key
    # Standard model string now works perfectly because we cleaned the environment!
    gemini_llm = LLM(
        model="gemini/gemini-3.1-flash-lite",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=api_key,
        temperature=0.2
    )

    # Digest automated baseline context elements
    income = agent1_json.get("income", 0.0)
    disposable_income = agent1_json.get("disposable_income", 0.0)
    financial_score = agent2_json.get("financial_score", 50)
    health_level = agent2_json.get("health_level", "Needs Improvement")
    
    recommended_saving = agent3_json.get("recommended_saving", 0.0)
    target_goal = agent3_json.get("goal", "Laptop")
    timeline_months = agent3_json.get("timeline_months", 10)

    # Assign core deployment capitalization pools
    monthly_investment_pool = recommended_saving if recommended_saving > 0 else max(disposable_income, 0.0)

    # TRIGGER LOGICAL INTERMEDIATE RAG LOOKUP
    rag_query = (
        f"Investment profiles appropriate for a financial health metric score of {financial_score} "
        f"with an allocation value of {monthly_investment_pool} across a target horizon of {timeline_months} months."
    )
    
    retrieved_knowledge_context = retrieve_knowledge(rag_query)

    context_payload = {
        "financial_profile": { "income": income, "disposable_income": disposable_income },
        "health_assessment": { "financial_score": financial_score, "health_level": health_level },
        "savings_plan_milestones": {
            "monthly_investment_pool": monthly_investment_pool,
            "target_goal": target_goal,
            "timeline_months": timeline_months
        },
        "retrieved_regulatory_and_knowledge_frameworks": retrieved_knowledge_context
    }

    # INITIALIZE SPECIALIZED AGENT CORE
    investment_agent = Agent(
        role="Investment Expert and Portfolio Strategist",
        goal="Parse financial inputs alongside RAG compliance contexts to generate structured educational asset options.",
        backstory=(
            "You are a certified technical wealth allocation planner. You interpret metrics using "
            "regulatory references (SEBI, RBI guides) inside your query load. Your output focus is giving "
            "clarity on risk matrices, security structures, and monthly compounding explanations."
        ),
        verbose=True,
        llm=gemini_llm
    )

    # Configure structural assignment constraints
    structuring_task = Task(
        description=(
            f"Analyze the combined incoming context payload object carefully:\n{json.dumps(context_payload, indent=2)}\n\n"
            "Execution Instructions:\n"
            f"1. Evaluate the available monthly capital investment pool of {monthly_investment_pool}.\n"
            "2. Generate exactly 5 to 6 distinct asset category paths (e.g., PPF, NPS, SGB, Diversified Index Funds, Fixed Deposits, Debt Funds).\n"
            "3. For EACH choice, provide: calculated monthly allocations, clear risk and security levels, a simple operational explanation, and key structural features.\n"
            "4. Analyze all 5-6 alternatives strictly against the retrieved RAG regulatory rules and select the single best matched option.\n"
            "5. Ensure the final result includes a standard educational compliance disclaimer."
        ),
        expected_output="A structured layout containing diverse investment alternatives and an optimized core recommendation selection.",
        agent=investment_agent,
        output_pydantic=InvestmentStrategySchema
    )

    crew = Crew(
        agents=[investment_agent],
        tasks=[structuring_task],
        process=Process.sequential
    )

    execution_output = crew.kickoff()

    # SECURE PYDANTIC TO JSON MATRIX DICTIONARY DUMP
    if hasattr(execution_output, 'pydantic') and execution_output.pydantic:
        return execution_output.pydantic.model_dump()

    if hasattr(execution_output, 'json_dict') and execution_output.json_dict:
        return execution_output.json_dict
    elif hasattr(execution_output, 'raw') and isinstance(execution_output.raw, str):
        try:
            return json.loads(execution_output.raw)
        except json.JSONDecodeError:
            pass
            
    if isinstance(execution_output, dict):
        return execution_output
        
    try:
        return json.loads(str(execution_output))
    except json.JSONDecodeError:
        return {"error": "Failed to map clean un-nested JSON data streams from terminal logic blocks."}