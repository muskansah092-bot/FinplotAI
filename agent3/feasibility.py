from typing import Dict, Any

def calculate_base_feasibility(agent1_data: Dict[str, Any], goal_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs fast, rule-based mathematical parsing of goal affordability[cite: 5].
    """
    disposable_income = float(agent1_data.get("disposable_income", 0))
    target_amount = float(goal_data.get("target_amount", 0))
    timeline = int(goal_data.get("timeline_months", 1))
    
    # Mathematical Required Saving Calculation[cite: 5]
    required_monthly = target_amount / timeline if timeline > 0 else target_amount
    
    # Base feasibility checking against disposable income[cite: 5]
    is_feasible = required_monthly <= disposable_income
    
    return {
        "monthly_saving_required": round(required_monthly, 2),
        "mathematically_feasible": is_feasible,
        "disposable_income": disposable_income
    }