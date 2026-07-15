import json

from agent1.prompts import TRANSACTION_PARSER_PROMPT


class LLMParser:

    def __init__(self, llm):
        self.llm = llm

    def parse(self, raw_text):

        prompt = TRANSACTION_PARSER_PROMPT.format(
            raw_text=raw_text
        )

        # -----------------------------
        # Call Gemini
        # -----------------------------
        try:
            response = self.llm.invoke(prompt)
        except Exception as e:
            raise RuntimeError(f"Failed to get response from Gemini: {e}")

        # -----------------------------
        # Validate response
        # -----------------------------
        content = response.content

        if not isinstance(content, list) or len(content) == 0:
            raise ValueError("Gemini returned an unexpected response format.")

        text = content[0].get("text", "")

        if not text:
            raise ValueError("Gemini returned an empty response.")

        # -----------------------------
        # Remove markdown if present
        # -----------------------------
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

        # -----------------------------
        # Convert JSON string -> Python
        # -----------------------------
        try:
            transactions = json.loads(text)
        except json.JSONDecodeError as e:
            print("\n========== INVALID JSON FROM GEMINI ==========")
            print(text)
            print("==============================================\n")
            raise ValueError(f"Gemini returned invalid JSON: {e}")

        # -----------------------------
        # Final validation
        # -----------------------------
        if not isinstance(transactions, list):
            raise ValueError("Expected a list of transactions.")

        return transactions