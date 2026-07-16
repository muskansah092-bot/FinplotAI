import json

with open("output/recommendation.json", "r", encoding="utf-8") as f:
    data = json.load(f)

required_keys = ["overall_score", "financial_summary", "priority_actions", "monthly_action_plan", "recommendations"]

for key in required_keys:
    if key not in data:
        print(f"MISSING KEY: {key}")
    else:
        print(f"OK: {key} -> {type(data[key]).__name__}")

# Extra checks
assert isinstance(data["overall_score"], (int, float)), "overall_score should be a number"
assert isinstance(data["priority_actions"], list), "priority_actions should be a list"
assert isinstance(data["monthly_action_plan"], list), "monthly_action_plan should be a list"
assert isinstance(data["recommendations"], list), "recommendations should be a list"

for item in data["monthly_action_plan"]:
    assert "month" in item and "action" in item, "each monthly_action_plan item needs 'month' and 'action'"

print("\nAll validation checks passed!")