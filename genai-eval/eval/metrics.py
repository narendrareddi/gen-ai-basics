from sklearn.metrics.pairwise import cosine_similarity
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
load_dotenv()

# Semantic similarity using Gemini embeddings
embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def exact_match(pred, expected):
    return expected.lower() in pred.lower()

def semantic_sim(pred, expected):
    pred_vec = embedder.embed_query(pred)
    exp_vec = embedder.embed_query(expected)
    return cosine_similarity([pred_vec], [exp_vec])[0][0]
