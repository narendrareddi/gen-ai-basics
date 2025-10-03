def estimate_cost(input_tokens, output_tokens, model="gemini-2.0-flash"):
    # Sample Gemini pricing (adjust to real values!)
    pricing = {
        "gemini-2.0-flash": {"input": 0.0001/1000, "output": 0.0003/1000}
    }
    rate = pricing[model]
    return (input_tokens * rate["input"]) + (output_tokens * rate["output"])
