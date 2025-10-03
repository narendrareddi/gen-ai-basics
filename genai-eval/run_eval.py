import json
import pandas as pd
from eval.harness import load_prompt, run_eval

# Load dataset
with open("data/eval_dataset.json", "r") as f:
    eval_data = json.load(f)

# Load prompts
prompt_v1 = load_prompt("prompts/v1.yaml")
prompt_v2 = load_prompt("prompts/v2.yaml")

# Run evaluations
results_v1 = run_eval(prompt_v1, eval_data, "v1")
results_v2 = run_eval(prompt_v2, eval_data, "v2")

# Combine
df = pd.DataFrame(results_v1 + results_v2)

# Save logs
df.to_csv("eval_results.csv", index=False)

print("=== Detailed Results ===")
print(df.to_string(index=False))

print("\n=== Accuracy (Exact Match) ===")
print(df.groupby("version")["exact_match"].mean())

print("\n=== LLM-as-Judge Score ===")
print(df.groupby("version")["judge_score"].mean())

print("\n=== Human Review Flags ===")
print(df.groupby("version")["human_review"].sum())

print("\n=== Latency (s) ===")
print(df.groupby("version")["latency"].mean())

print("\n=== Cost (USD) ===")
print(df.groupby("version")["cost_usd"].sum())
