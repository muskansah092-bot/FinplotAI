"""agent5/memory.py"""


class ConversationMemory:
    """
    Simple in-session memory for Agent 5.

    Holds everything Agent 5 needs to remember during a single
    user conversation: what the user is trying to do, what inputs
    they've already given, and what each downstream agent has
    already produced.

    This is intentionally just a dict wrapper — no database,
    no persistence across sessions. One instance per conversation.
    """

    def __init__(self):
        # What the user is currently trying to accomplish.
        # One of: "financial_analysis", "goal_planning",
        # "investment_advice", "general_question", or None.
        self.intent = None

        # Raw inputs collected from the user so far.
        self.collected_inputs = {
            "file_path": None,       # path to uploaded PDF/image/CSV
            "manual_data": None,     # manual transaction entry text
            "goal": None,
            "target_amount": None,
            "timeline_months": None,
            "_pending_field": None,
        }

        # Outputs produced by each agent during this session.
        self.agent_outputs = {
            "agent1": None,   # transactions list
            "agent2": None,   # financial health dict
            "agent3": None,   # savings plan dict
            "agent4": None,   # investment plan dict
        }

        # Full chat history: list of {"role": "user"/"assistant", "content": str}
        self.chat_history = []

    # -----------------------------------------------------
    # Input helpers
    # -----------------------------------------------------

    def set_input(self, key: str, value):
        if key not in self.collected_inputs:
            raise KeyError(f"Unknown input key: {key}")
        self.collected_inputs[key] = value

    def get_input(self, key: str):
        return self.collected_inputs.get(key)

    def missing_inputs(self, required_keys: list) -> list:
        """Return which of the required keys are still missing."""
        return [
            key for key in required_keys
            if self.collected_inputs.get(key) in (None, "", [])
        ]

    # -----------------------------------------------------
    # Agent output helpers
    # -----------------------------------------------------

    def set_agent_output(self, agent_name: str, output):
        if agent_name not in self.agent_outputs:
            raise KeyError(f"Unknown agent: {agent_name}")
        self.agent_outputs[agent_name] = output

    def get_agent_output(self, agent_name: str):
        return self.agent_outputs.get(agent_name)

    def has_run(self, agent_name: str) -> bool:
        return self.agent_outputs.get(agent_name) is not None

    # -----------------------------------------------------
    # Chat history helpers
    # -----------------------------------------------------

    def add_message(self, role: str, content: str):
        self.chat_history.append({"role": role, "content": content})

    def get_history(self) -> list:
        return self.chat_history

    # -----------------------------------------------------
    # Reset
    # -----------------------------------------------------

    def reset(self):
        self.__init__()