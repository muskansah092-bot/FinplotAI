from recommendation import generate_recommendation
from utils import save_json
import json

OUTPUT_PATH = "output/recommendation.json"


def clean_response_text(text):
    """
    Gemini sometimes wraps JSON in ```json ... ``` markdown fences.
    This function removes those fences if present, so the text
    can be safely parsed as JSON.
    """
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return text.strip()


def main():
    print("Generating financial recommendation...")

    raw_response = generate_recommendation()
    cleaned_text = clean_response_text(raw_response)

    recommendation_data = json.loads(cleaned_text)

    print("---- RECOMMENDATION ----")
    print(json.dumps(recommendation_data, indent=4))

    save_json(recommendation_data, OUTPUT_PATH)
    print(f"Saved recommendation to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()