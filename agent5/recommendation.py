from utils import load_json, read_text_file
from prompts import build_recommendation_prompt
from llm import generate_response
import os

# Paths to the 4 agent input files
AGENT1_PATH = "sample_inputs/agent1_output.json"
AGENT2_PATH = "sample_inputs/agent2_output.json"
AGENT3_PATH = "sample_inputs/agent3_output.json"
AGENT4_PATH = "sample_inputs/agent4_output.json"

# Folder containing financial knowledge text files
KNOWLEDGE_FOLDER = "knowledge"


def load_all_knowledge():
    """
    Reads every .txt file inside the knowledge/ folder
    and combines them into one big string.
    """
    combined_text = ""
    for filename in os.listdir(KNOWLEDGE_FOLDER):
        if filename.endswith(".txt"):
            file_path = os.path.join(KNOWLEDGE_FOLDER, filename)
            combined_text += read_text_file(file_path)
            combined_text += "\n\n"
    return combined_text


def generate_recommendation(agent1_path=AGENT1_PATH, agent2_path=AGENT2_PATH,
                             agent3_path=AGENT3_PATH, agent4_path=AGENT4_PATH):
    """
    Runs the full Agent 5 workflow:
    1. Load all 4 agent JSON outputs
    2. Load financial knowledge text files
    3. Build the Gemini prompt
    4. Send it to Gemini and return the raw text response
    """
    agent1_data = load_json(agent1_path)
    agent2_data = load_json(agent2_path)
    agent3_data = load_json(agent3_path)
    agent4_data = load_json(agent4_path)

    knowledge_text = load_all_knowledge()

    prompt = build_recommendation_prompt(
        agent1_data, agent2_data, agent3_data, agent4_data, knowledge_text
    )

    response_text = generate_response(prompt)
    return response_text