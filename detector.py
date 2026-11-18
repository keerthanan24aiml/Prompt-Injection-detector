
import re
import time
import unicodedata
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# 1. Model configuration
MODEL_NAME = "Horizon-Labs/prompt-injection-guard-small"
ML_THRESHOLD = 0.80

tokenizer = None
model = None
injection_label_id = None
model_error = None

# 2. Normalize input
def normalize_text(text):
    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# 3. Suspicious patterns
INJECTION_PATTERNS = [
    r"ignore all previous instructions",
    r"disregard (all )?(previous|prior|system) instructions",
    r"reveal (the )?(hidden )?(system prompt|instructions)",
    r"show me (the )?(hidden )?system prompt",
    r"bypass (all )?safety rules",
    r"override (all )?(previous )?instructions",
    r"act as (an )?(unrestricted|uncensored) (ai|assistant)",
    r"forget (all )?(previous )?instructions",
]


# 4. Rule-based detection
def detect_with_rules(text):
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text):
            return True, pattern

    return False, None

def is_educational_mention(text):
    """Identify clearly framed educational or research discussions."""

    text = text.strip().lower()

    # The message must be framed as an educational request.
    educational_request = re.search(
        r"^(explain|describe|discuss|analyse|analyze|"
        r"write|define|what does|why do|how do)\b",
        text
    )

    # It must contain an educational or security-research context.
    educational_context = re.search(
        r"\b(prompt injection|cybersecurity|security research|"
        r"academic|educational|research|lecture|"
        r"attackers use|defensive security)\b",
        text
    )

    # The suspicious phrase must be discussed as a topic.
    attack_phrase = re.search(
        r"\b(ignore all previous instructions|"
        r"disregard previous instructions)\b",
        text
    )

    return bool(
        educational_request
        and educational_context
        and attack_phrase
    )
# 5. Load ML model only once
def load_ml_model():
    global tokenizer, model, injection_label_id, model_error

    if model is not None:
        return True

    if model_error is not None:
        return False

    try:
        print("Loading prompt injection ML model...")

        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

        # Verify which class represents an injection
        labels = model.config.id2label

        injection_ids = [
            int(label_id)
            for label_id, label in labels.items()
            if "INJECTION" in str(label).upper()
        ]

        if len(injection_ids) != 1:
            raise ValueError(
                f"Could not identify injection label: {labels}"
            )

        injection_label_id = injection_ids[0]

        model.eval()
        model.to("cpu")

        print("ML model loaded successfully!")
        print("Model labels:", labels)

        return True

    except Exception as error:
        model_error = str(error)
        print("ML model loading failed:", model_error)
        return False


# 6. Get injection probability from ML model
def detect_with_ml(text):
    if not load_ml_model():
        return None

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    with torch.inference_mode():
        outputs = model(**inputs)
        probabilities = torch.softmax(outputs.logits, dim=-1)

    injection_probability = probabilities[0][injection_label_id].item()

    return injection_probability


# 7. Main detection function
def analyze_prompt(text):
    start_time = time.perf_counter()

    def make_result(decision, score, confidence, reason, detected_by):
        latency = (time.perf_counter() - start_time) * 1000

        return {
            "decision": decision,
            "risk_score": round(score, 2),
            "confidence": round(confidence, 4),
            "reason": reason,
            "detected_by": detected_by,
            "latency_ms": round(latency, 2)
        }

    # Validate input
    if not isinstance(text, str) or not text.strip():
        return make_result(
            "BLOCK", 100, 1.0,
            "Empty or invalid input", "rules"
        )

    if len(text) > 10000:
        return make_result(
            "BLOCK", 100, 1.0,
            "Input exceeds maximum allowed length", "rules"
        )

    cleaned_text = normalize_text(text)

    # Check for a known educational mention
    if is_educational_mention(cleaned_text):
        return make_result(
        "ALLOW",
        5.0,
        0.95,
        "Educational discussion of an injection phrase",
        "context"
    )

    # Run rule detection
    is_injection, matched_pattern = detect_with_rules(cleaned_text)

    # Run ML detection
    ml_probability = detect_with_ml(cleaned_text)

    # Combine results
    rule_score = 0.95 if is_injection else 0.0
    ml_score = ml_probability if ml_probability is not None else 0.0

    risk_score = max(rule_score, ml_score) * 100

    if is_injection:
        decision = "BLOCK"
        reason = f"Suspicious instruction detected: {matched_pattern}"
        detected_by = "combined" if ml_probability is not None else "rules"
        confidence = max(rule_score, ml_score)

    elif ml_probability is not None and ml_probability >= ML_THRESHOLD:
        decision = "BLOCK"
        reason = f"ML classifier detected injection ({ml_probability:.2%})"
        detected_by = "ml"
        confidence = ml_probability

    else:
        decision = "ALLOW"
        reason = (
            "No suspicious pattern or high ML risk detected"
            if ml_probability is not None
            else "Rules-only: ML model unavailable"
        )
        detected_by = "none" if ml_probability is not None else "rules"
        confidence = 1 - ml_score if ml_probability is not None else 0.0

    return make_result(
        decision,
        risk_score,
        confidence,
        reason,
        detected_by
    )
