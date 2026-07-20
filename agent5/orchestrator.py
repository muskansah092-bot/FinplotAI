"""agent5/orchestrator.py"""
from agent5.intent_classifier import classify_intent
from agent5 import integrations
from agent5.slot_filler import extract_field
from agent5.response_generator import generate_response
from agent5.rag.simple_rag import answer_general_question

REQUIRED_INPUTS = {
    "financial_analysis": ["transaction_data"],
    "goal_planning": ["transaction_data", "goal", "target_amount", "timeline_months"],
    "investment_advice": ["transaction_data", "goal", "target_amount", "timeline_months"],
    "general_question": [],
}

FOLLOWUP_QUESTIONS = {
    "transaction_data": (
        "To get started, please share your financial data — you can upload "
        "a bank statement PDF, a passbook image, a UPI screenshot, or just "
        "type your transactions manually."
    ),
    "goal": "What's your financial goal? (e.g., buying a laptop, building an emergency fund)",
    "target_amount": "What's the target amount you're aiming to save?",
    "timeline_months": "Over how many months would you like to achieve this goal?",
}


def _has_transaction_data(memory) -> bool:
    return bool(memory.get_input("file_path") or memory.get_input("manual_data"))


def _get_missing_fields(memory, intent: str) -> list:
    required = REQUIRED_INPUTS.get(intent, [])
    missing = []

    for field in required:
        if field == "transaction_data":
            if not _has_transaction_data(memory):
                missing.append(field)
        else:
            if memory.get_input(field) in (None, ""):
                missing.append(field)

    return missing


def _run_agent_chain(memory, intent: str) -> dict:
    """
    Runs the correct sequence of agents based on intent, using
    whatever transaction input the user gave (file takes priority
    over manual text if somehow both are set).
    """
    file_path = memory.get_input("file_path")
    manual_data = memory.get_input("manual_data")

    if file_path:
        transactions = integrations.run_agent1_from_file(file_path)
    else:
        transactions = integrations.run_agent1_from_manual(manual_data)
    memory.set_agent_output("agent1", transactions)

    # NOTE: passing transactions in explicitly now — Agent 2's own
    # run_agent2() reads a file path that never matches where Agent 1's
    # output actually gets saved (see integrations.py for details).
    agent2_output = integrations.run_agent2(transactions)
    memory.set_agent_output("agent2", agent2_output)

    if intent in ("goal_planning", "investment_advice"):
        goal_data = {
            "goal": memory.get_input("goal"),
            "target_amount": memory.get_input("target_amount"),
            "timeline_months": memory.get_input("timeline_months"),
        }
        agent3_output = integrations.run_agent3(transactions, agent2_output, goal_data)
        memory.set_agent_output("agent3", agent3_output)

    if intent == "investment_advice":
        agent4_output = integrations.run_agent4(
            transactions, agent2_output, memory.get_agent_output("agent3")
        )
        memory.set_agent_output("agent4", agent4_output)

    result = {
        "transactions": memory.get_agent_output("agent1"),
        "agent2": memory.get_agent_output("agent2"),
        "agent3": memory.get_agent_output("agent3"),
        "agent4": memory.get_agent_output("agent4"),
    }

    integrations.save_agent5_output(result)

    return result


def handle_message(memory, user_message: str) -> dict:
    memory.add_message("user", user_message)

    if memory.intent is None:
        context = "\n".join(m["content"] for m in memory.get_history()[-6:])
        memory.intent = classify_intent(user_message, context=context)

    intent = memory.intent

    if intent == "general_question":
        reply_text = answer_general_question(user_message)
        memory.add_message("assistant", reply_text)
        return {"type": "general", "text": reply_text}

    # If we were waiting on a specific field, try to extract it
    # from THIS message before checking what's still missing.
    """Change in agent5/orchestrator.py — inside handle_message(), replace this block:"""

    pending_field = memory.get_input("_pending_field")
    if pending_field == "transaction_data":
        # User typed transactions directly in chat rather than
        # uploading a file. Only capture it if no file was already
        # uploaded via the /upload endpoint for this session.
        if not _has_transaction_data(memory):
            memory.set_input("manual_data", user_message)
    elif pending_field:
        value = extract_field(pending_field, user_message)
        if value is not None:
            memory.set_input(pending_field, value)

    missing = _get_missing_fields(memory, intent)

    if missing:
        next_field = missing[0]
        memory.set_input("_pending_field", next_field)
        question = FOLLOWUP_QUESTIONS[next_field]
        memory.add_message("assistant", question)
        return {"type": "question", "text": question}

    memory.set_input("_pending_field", None)
    data = _run_agent_chain(memory, intent)
    reply_text = generate_response(intent, data)
    memory.add_message("assistant", reply_text)
    return {"type": "result", "intent": intent, "text": reply_text, "data": data}