import streamlit as st
import pandas as pd
import altair as alt
from eval.harness import load_prompt
from langchain_google_genai import ChatGoogleGenerativeAI
from eval.metrics import semantic_sim, exact_match
from eval.judge import llm_as_judge
from eval.guardrails import contains_pii, enforce_safe_answer
from eval.human_review import human_review_needed
import time

# -----------------------------
# Setup LLM & Prompts
# -----------------------------
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

prompt_v1 = load_prompt("prompts/v1.yaml")
prompt_v2 = load_prompt("prompts/v2.yaml")

# -----------------------------
# Load Offline Eval Data
# -----------------------------
@st.cache_data
def load_data():
    return pd.read_csv("eval_results.csv")

df = load_data()

st.title("📊 GenAI Prompt Evaluation Dashboard")
st.write("Compare prompt versions on accuracy, cost, latency, and review flags.")

# -----------------------------
# Overall Metrics
# -----------------------------
st.header("Overall Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Accuracy (Exact)", f"{df['exact_match'].mean():.2f}")
col2.metric("LLM-as-Judge", f"{df['judge_score'].mean():.2f}")
col3.metric("Avg Latency (s)", f"{df['latency'].mean():.2f}")
col4.metric("Total Cost (USD)", f"{df['cost_usd'].sum():.4f}")

# -----------------------------
# Comparison by Prompt Version
# -----------------------------
st.header("Prompt Version Comparison")
metrics = ["exact_match", "semantic_sim", "judge_score", "latency", "cost_usd"]
agg_df = df.groupby("version")[metrics].mean().reset_index()

chart = alt.Chart(agg_df).transform_fold(
    metrics,
    as_=["Metric", "Value"]
).mark_bar().encode(
    x="version:N",
    y="Value:Q",
    color="Metric:N",
    column="Metric:N"
).properties(width=150)

st.altair_chart(chart)

# -----------------------------
# Human Review Flags
# -----------------------------
st.header("Human Review Flags")
review_counts = df.groupby("version")["human_review"].sum().reset_index()
st.bar_chart(review_counts.set_index("version"))

# -----------------------------
# Detailed Results Table
# -----------------------------
st.header("Detailed Evaluation Results")
filter_version = st.multiselect("Filter by version", df["version"].unique(), default=df["version"].unique())
filtered = df[df["version"].isin(filter_version)]
st.dataframe(filtered, width='stretch')

st.subheader("⚠️ Samples Needing Human Review")
flagged = filtered[filtered["human_review"] == True]
st.dataframe(flagged, width='stretch')

# -----------------------------
# Real-Time Evaluation Section
# -----------------------------
st.header("⚡ Real-Time Evaluation")

with st.form("live_eval_form"):
    user_question = st.text_input("Enter a question for live testing:")
    user_context = st.text_area("Optional: Add context (for prompts that expect it)", "")
    user_expected = st.text_area("Optional: Add expected answer (for scoring)", "")
    submit_button = st.form_submit_button("Run Evaluation")

if submit_button and user_question.strip():
    st.write("Running evaluation...")

    results = []
    for version, prompt in [("v1", prompt_v1), ("v2", prompt_v2)]:
        chain = prompt | llm

        # Detect required input variables dynamically
        variables = prompt.input_variables  # Already a list of strings
        inputs = {}
        if "question" in variables:
            inputs["question"] = user_question
        if "context" in variables:
            inputs["context"] = user_context.strip() if user_context.strip() else "No relevant info."

        # Run LLM
        start = time.time()
        response = chain.invoke(inputs)
        latency = time.time() - start
        output = response.content.strip()

        # Apply guardrails
        if contains_pii(output):
            output = "[REDACTED: PII Detected]"
        output = enforce_safe_answer(output, inputs.get("context", ""))

        # Metrics
        if user_expected.strip():
            sim = semantic_sim(output, user_expected)
            acc = exact_match(output, user_expected)
            judge = llm_as_judge(user_question, output, user_expected)
        else:
            sim = semantic_sim(output, user_question)
            acc = None
            judge = llm_as_judge(user_question, output, user_question)

        review_flag = human_review_needed(output, user_question, sim)

        results.append({
            "version": version,
            "inputs": inputs,
            "output": output,
            "latency": round(latency, 2),
            "semantic_sim": round(sim, 3),
            "exact_match": acc,
            "judge_score": judge,
            "human_review": review_flag
        })

    st.subheader("🔎 Side-by-Side Comparison of Prompts")
    st.dataframe(pd.DataFrame(results), width='stretch')
