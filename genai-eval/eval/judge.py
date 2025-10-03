from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()

judge_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

judge_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an evaluator.
You will receive a question, a model answer, and the expected answer.
Grade the model answer:
- 1 if it matches OR is factually correct/semantically equivalent.
- 0 if it is wrong or hallucinated.
Reply ONLY with 1 or 0.
    """),
    ("user", "Question: {question}\nModel Answer: {output}\nExpected: {expected}")
])

def llm_as_judge(question, output, expected):
    chain = judge_prompt | judge_llm
    response = chain.invoke({"question": question, "output": output, "expected": expected})
    score = response.content.strip()
    return int(score) if score in ["0","1"] else 0
