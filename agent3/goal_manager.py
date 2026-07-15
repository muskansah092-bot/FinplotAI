from typing import List
from pydantic import BaseModel, Field

class GoalInputSchema(BaseModel):
    goal: str = Field(description="Name of the financial goal (e.g., Laptop, Emergency Fund).")
    target_amount: float = Field(description="Total target amount in currency.")
    timeline_months: int = Field(description="Target timeline to finish the goal in months[cite: 5].")

class SavingsPlanSchema(BaseModel):
    goal: str = Field(description="The financial goal selected by the user[cite: 5].")
    target_amount: float = Field(description="The total target amount required[cite: 5].")
    timeline_months: int = Field(description="The duration in months[cite: 5].")
    monthly_saving_required: float = Field(description="Target amount divided by timeline[cite: 5].")
    goal_feasible: bool = Field(description="True if the monthly saving requirement is realistically affordable[cite: 5].")
    recommended_saving: float = Field(description="The optimized suggested monthly savings amount[cite: 5].")
    expense_reductions: List[str] = Field(description="Specific discretionary categories targeted for reductions[cite: 5].")
    roadmap: str = Field(description="A sequential timeline roadmap outline[cite: 5].")