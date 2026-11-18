from detector import detect_with_rules, detect_with_ml, normalize_text

prompt = "Explain why the phrase 'ignore all previous instructions' is used in prompt injection research."

cleaned_prompt = normalize_text(prompt)

rule_result = detect_with_rules(cleaned_prompt)
ml_probability = detect_with_ml(cleaned_prompt)

print("Prompt:", prompt)
print("Rule result:", rule_result)
print("ML probability:", ml_probability)