import os
import json
import sys

# Ensure Python respects root path mapping patterns inside the script folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from investment_agent import run_agent4_pipeline

def execute_investment_agent_test():
    print("=" * 70)
    print("   RUNNING DYNAMIC RAG INTEGRATION PASS FOR AGENT 4  ")
    print("=" * 70)

    if not os.environ.get("GEMINI_API_KEY"):
        print("\n[CRITICAL ERROR] Halted: Missing GEMINI_API_KEY environment token!")
        return

    # Dynamic path routing to the base workspace outputs workspace
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(root_dir, "outputs")
    
    agent1_path = os.path.join(output_dir, "transactions.json")
    agent2_path = os.path.join(output_dir, "agent2_output.json")
    
    # Adaptive matching logic for your chosen filename from the prior pass
    agent3_path = os.path.join(output_dir, "agent3_output.json")
    if not os.path.exists(agent3_path):
        agent3_path = os.path.join(output_dir, "goal_plan.json")
        
    output_file_path = os.path.join(output_dir, "agent4_output.json")

    try:
        if not os.path.exists(agent1_path) or not os.path.exists(agent2_path) or not os.path.exists(agent3_path):
            raise FileNotFoundError("Upstream files missing within systemic output arrays!")

        # Ingest live tracking outputs dynamically
        with open(agent1_path, "r", encoding="utf-8") as f1:
            raw_a1 = json.load(f1)
        with open(agent2_path, "r", encoding="utf-8") as f2:
            live_a2 = json.load(f2)
        with open(agent3_path, "r", encoding="utf-8") as f3:
            live_a3 = json.load(f3)

        # Parse transaction structures seamlessly
        income, expenses = 0.0, 0.0
        for txn in raw_a1:
            amt = float(txn.get("amount", 0.0))
            if txn.get("type") == "Credit":
                income += amt
            else:
                expenses += amt

        live_a1 = {
            "income": round(income, 2),
            "disposable_income": round(income - expenses, 2)
        }

        print("[INFO] Passing parameters into RAG-linked pipeline execution engine...")
        
        # Fire up your operational agent pipeline loop
        final_strategy_output = run_agent4_pipeline(
            agent1_json=live_a1,
            agent2_json=live_a2,
            agent3_json=live_a3
        )

        # Write output natively in professional format to root outputs folder
        os.makedirs(output_dir, exist_ok=True)
        with open(output_file_path, "w", encoding="utf-8") as out_file:
            json.dump(final_strategy_output, out_file, indent=4)

        print("\n" + "=" * 70)
        print("   SUCCESS: DIVERSIFIED PORTFOLIO SCHEMAS PERSISTED SEAMLESSLY  ")
        print("=" * 70)
        print(json.dumps(final_strategy_output, indent=4))
        print(f"\n💾 [EXPORT SUCCESS] Target file saved neatly to: {output_file_path}\n")

    except Exception as e:
        print(f"\n[RUN RUNTIME BREAKDOWN] Validation chain failed: {str(e)}")

if __name__ == "__main__":
    execute_investment_agent_test()