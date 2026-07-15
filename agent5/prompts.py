def build_recommendation_prompt(agent1_data, agent2_data, agent3_data, agent4_data, knowledge_text):
    """
    Builds the full prompt sent to Gemini.
    Combines all 4 agent outputs + financial knowledge text,
    and instructs Gemini to return a specific JSON structure.
    """

    prompt = f"""
You are a professional financial advisor AI.

Analyze the following data about a user and generate personalized financial recommendations.

===============================
1. FINANCIAL PROFILE (Agent 1)
===============================
{agent1_data}

===============================
2. FINANCIAL HEALTH (Agent 2)
===============================
{agent2_data}

===============================
3. SAVINGS GOAL (Agent 3)
===============================
{agent3_data}

===============================
4. INVESTMENT RECOMMENDATION (Agent 4)
===============================
{agent4_data}

===============================
5. FINANCIAL KNOWLEDGE BASE
===============================
{knowledge_text}

===============================
YOUR TASK
===============================
Using ALL the information above, do the following:

1. Analyze the user's financial profile, financial health, savings goal, and investment plan together.
2. Use the financial knowledge base as guidance for best practices (do not just copy it, apply it to this user's situation).
3. Generate an overall financial score (0-100).
4. Write a short financial summary (2-4 sentences) of the user's current situation.
5. Generate a list of 3-5 priority actions the user should take first.
6. Generate a month-wise action plan for the next 6 months (1 action per month).
7. Generate a list of 3-5 general recommendations for improving their finances.

===============================
OUTPUT FORMAT
===============================
Return ONLY valid JSON. Do not include any explanation, markdown formatting, or code fences.
Use exactly this structure:

{{
  "overall_score": 68,
  "financial_summary": "...",
  "priority_actions": ["...", "...", "..."],
  "monthly_action_plan": [
    {{"month": 1, "action": "..."}},
    {{"month": 2, "action": "..."}}
  ],
  "recommendations": ["...", "..."]
}}
"""
    return prompt