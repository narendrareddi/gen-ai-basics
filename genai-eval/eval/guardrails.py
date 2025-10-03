import re
import json

def contains_pii(text):
    patterns = [
        r"\b\d{3}-\d{2}-\d{4}\b",   # SSN
        r"\b\d{10}\b",              # phone
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z]{2,}",  # email
        r"\b\d{16}\b"               # credit card
    ]
    return any(re.search(p, text) for p in patterns)

def enforce_safe_answer(output, context):
    if "I don’t know" in output:
        return output
    if context.strip().lower() == "no relevant info." and "I don’t know" not in output:
        return "I don’t know"
    return output

def enforce_json_schema(output):
    try:
        json.loads(output)
        return output
    except:
        return '{"error": "Invalid JSON"}'
