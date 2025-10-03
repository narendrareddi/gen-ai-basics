import time
import json
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from .metrics import exact_match, semantic_sim
from .cost_tracker import estimate_cost
from .judge import llm_as_judge
from .human_review import human_review_needed
from .guardrails import contains_pii, enforce_safe_answer
from dotenv import load_dotenv
load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

def run_eval(prompt, dataset, version):
    results = []
    chain = prompt | llm

    for sample in dataset:
        if "context" in sample:
            inputs = {"question": sample["question"], "context": sample["context"]}
        else:
            inputs = {"question": sample["question"]}

        start = time.time()
        response = chain.invoke(inputs)
        latency = time.time() - start

        output = response.content.strip()
        expected = sample["expected"]

        # Guardrails
        if contains_pii(output):
            output = "[REDACTED: PII Detected]"
        output = enforce_safe_answer(output, sample.get("context",""))

        # Metrics
        acc = exact_match(output, expected)
        sim = semantic_sim(output, expected)
        judge_score = llm_as_judge(sample["question"], output, expected)
        needs_review = human_review_needed(output, expected, sim)

        # Cost estimate
        cost = estimate_cost(response.usage_metadata['input_tokens'], response.usage_metadata['output_tokens'])

        results.append({
            "version": version,
            "question": sample["question"],
            "context": sample.get("context", ""),
            "expected": expected,
            "output": output,
            "exact_match": acc,
            "semantic_sim": round(sim, 3),
            "judge_score": judge_score,
            "human_review": needs_review,
            "latency": round(latency, 2),
            "cost_usd": round(cost, 6)
        })
    return results

def load_prompt(yaml_file):
    import yaml
    with open(yaml_file, "r") as f:
        d = yaml.safe_load(f)
    return ChatPromptTemplate.from_messages([
        ("system", d["system"]),
        ("user", d["user"])
    ])