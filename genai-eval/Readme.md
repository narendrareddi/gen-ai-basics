# GenAI Evaluation Dashboard

A **Streamlit-based evaluation framework** for comparing and analyzing Generative AI prompt versions in real-time and offline. Supports **LLM-as-Judge**, **human review flags**, **guardrails**, and **prompt versioning**. Built with **Google Gemini 2.0 Flash**.

---

## 🚀 Features

### 1. Prompt Engineering
- Supports multiple prompt versions (`v1`, `v2`) with dynamic input handling.
- Handles question-only and context+question prompts.
- Real-time side-by-side comparison of different prompts.

### 2. Evaluation & Observability
- Offline evaluation from `eval_results.csv`:
  - Accuracy (`exact_match`)
  - Semantic similarity
  - LLM-as-Judge score
  - Latency
  - Cost
  - Human review flags
- Real-time evaluation with optional expected output for proper scoring.
- Guardrails for **PII / unsafe outputs**.
- Metrics visualization using **Altair**.

### 3. Human-in-the-Loop & Guardrails
- Human review flags for uncertain or low-confidence outputs.
- Guardrails for safety, fact verification, and PII detection.
- Configurable evaluation functions to integrate human feedback.

### 4. Dashboard & A/B Testing
- Streamlit dashboard for offline & live evaluation.
- Compare prompt versions for latency, cost, and output quality.
- Optional expected answer input for live evaluation metrics.
- Future-ready for traffic split / A/B testing simulation.

---

### 5. How It Works

Load prompts using load_prompt() function.
Send inputs to LLM (ChatGoogleGenerativeAI) based on prompt schema.
Evaluate outputs:
Semantic similarity to expected answer
Exact match (optional)
LLM-as-Judge (numeric 0/1)
Human review flag
Latency and cost
Apply guardrails for safety and PII.
Display metrics and outputs in Streamlit dashboard.