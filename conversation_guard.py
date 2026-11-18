
import re
from detector import analyze_prompt

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Stores conversation information separately for each session.
conversation_memory = {}

MAX_TURNS = 20

# Load the semantic model once when the module is imported.
semantic_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


# Security-related behaviour patterns.
ATTACK_SIGNALS = {
    "instruction_override": [
        r"\bignore\b.{0,50}\b(instructions|rules|guidelines)\b",
        r"\bdisregard\b.{0,50}\b(instructions|rules)\b",
        r"\boverride\b.{0,50}\b(instructions|rules)\b",
        r"\bforget\b.{0,50}\b(instructions|rules)\b",
    ],
    "role_manipulation": [
        r"\bact as\b.{0,50}\b(unrestricted|uncensored|admin)\b",
        r"\byou are now\b.{0,50}\b(unrestricted|developer|admin)\b",
    ],
    "confidential_data_extraction": [
        r"\breveal\b.{0,50}\b(hidden|system|secret|confidential)\b",
        r"\bshow\b.{0,50}\b(hidden|system)\b.{0,20}\b(prompt|instructions)\b",
        r"\bprint\b.{0,50}\b(confidential|secret|system)\b",
    ],
    "safety_bypass": [
        r"\bbypass\b.{0,50}\b(safety|security|restrictions)\b",
        r"\bdisable\b.{0,50}\b(safety|security|restrictions)\b",
    ]
}


def find_attack_signals(text):
    """Find security-related signals in a single conversation turn."""

    text = text.lower()
    detected = []

    for category, patterns in ATTACK_SIGNALS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                detected.append(category)
                break

    return detected


def calculate_intent_drift(original_intent, current_prompt):
    """Measure semantic deviation from the original conversation intent."""

    embeddings = semantic_model.encode(
        [original_intent, current_prompt]
    )

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    # Keep the score within the 0-100 range.
    drift_score = (1 - similarity) * 100
    drift_score = max(0.0, min(100.0, drift_score))

    return round(float(drift_score), 2)


def analyze_conversation(session_id, user_prompt):
    """
    Analyse the current prompt and its conversation history.
    Combines hybrid prompt detection, semantic intent tracking,
    and conversation-level attack evidence.
    """

    if not isinstance(session_id, str) or not session_id.strip():
        raise ValueError("A valid session_id is required.")

    if not isinstance(user_prompt, str) or not user_prompt.strip():
        raise ValueError("A non-empty user prompt is required.")

    # Create a separate memory for a new session.
    if session_id not in conversation_memory:
        conversation_memory[session_id] = {
            "original_intent": user_prompt,
            "turns": [],
            "total_turns": 0
        }

    session = conversation_memory[session_id]

    # Assign a permanent turn number.
    session["total_turns"] += 1
    turn_number = session["total_turns"]

    # Compare the current message with the original intent.
    intent_drift_score = calculate_intent_drift(
        session["original_intent"],
        user_prompt
    )

    # Analyse the current prompt using the existing detector.
    individual_result = analyze_prompt(user_prompt)

   # Identify security-related signals.
# Do not record attack signals for prompts classified
# as legitimate educational discussions.
    if individual_result["detected_by"] == "context":
        signals = []
    else:
        signals = find_attack_signals(user_prompt)
    current_turn = {
        "turn": turn_number,
        "message": user_prompt,
        "signals": signals,
        "decision": individual_result["decision"],
        "intent_drift_score": intent_drift_score
    }

    session["turns"].append(current_turn)

    # Keep only the most recent turns for conversation analysis.
    session["turns"] = session["turns"][-MAX_TURNS:]

    # Record which turns contain each security signal.
    signal_evidence = {}

    for turn in session["turns"]:
        for signal in turn["signals"]:
            signal_evidence.setdefault(signal, []).append(
                turn["turn"]
            )

    all_signals = set(signal_evidence.keys())

    # Check whether related attack behaviours occurred
    # across different conversation turns.
    def occurred_across_turns(signal_a, signal_b):
        turns_a = set(signal_evidence.get(signal_a, []))
        turns_b = set(signal_evidence.get(signal_b, []))

        return any(
            turn_a != turn_b
            for turn_a in turns_a
            for turn_b in turns_b
        )

    multi_turn_attack = (
        occurred_across_turns(
            "instruction_override",
            "confidential_data_extraction"
        )
        or occurred_across_turns(
            "instruction_override",
            "safety_bypass"
        )
    )

    # Preserve the existing detector's BLOCK decision.
    if individual_result["decision"] == "BLOCK":
        decision = "BLOCK"
        reason = individual_result["reason"]

    elif multi_turn_attack:
        decision = "BLOCK"
        reason = (
            "Related security attack behaviours were detected "
            "across multiple conversation turns."
        )

    else:
        decision = "ALLOW"
        reason = "No sufficient conversation-level attack evidence."

    # Identify the turns that contributed security signals.
    suspicious_turns = sorted({
        turn["turn"]
        for turn in session["turns"]
        if turn["signals"]
    })

    # Security risk is separate from semantic intent deviation.
    if multi_turn_attack and decision == "BLOCK":
        risk_score = max(
            individual_result["risk_score"],
            90.0
        )
    else:
        risk_score = individual_result["risk_score"]

    return {
        "decision": decision,
        "current_signals": signals,
        "risk_score": risk_score,
        "intent_drift_score": intent_drift_score,
        "original_intent": session["original_intent"],
        "suspicious_turns": suspicious_turns,
        "detected_signals": sorted(all_signals),
        "signal_evidence": signal_evidence,
        "reason": reason,
        "individual_result": individual_result
        
    }


def reset_conversation(session_id):
    """Clear the memory of a particular conversation."""

    conversation_memory.pop(session_id, None)
