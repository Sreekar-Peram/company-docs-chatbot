import os
import pickle
import faiss
from sentence_transformers import SentenceTransformer
import subprocess
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json


INDEX_PATH = "llmapi/index.faiss"
CHUNKS_PATH = "llmapi/chunks.pkl"

@csrf_exempt
def query_with_retrieval(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question = data.get("question", "")
            if not question:
                return JsonResponse({"error": "No question provided"}, status=400)
            
            answer = ask_question(question)
            return JsonResponse({"answer": answer})
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Only POST method allowed"}, status=405)
    
def load_index():
    if not (os.path.exists(INDEX_PATH) and os.path.exists(CHUNKS_PATH)):
        raise FileNotFoundError("Index or chunks metadata not found. Run the index builder first.")
    index = faiss.read_index(INDEX_PATH)
    with open(CHUNKS_PATH, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata

def retrieve_chunks(question, k=3):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    question_embedding = model.encode([question])
    index, metadata = load_index()

    D, I = index.search(question_embedding, k)
    # Return list of chunks with source info for context
    results = []
    for idx in I[0]:
        if idx < len(metadata):
            results.append(metadata[idx]["text"])
    return results

def format_prompt(chunks, question):
    context = "\n---\n".join(chunks)
    prompt = f"""
You are a helpful assistant. Use ONLY the following context to answer the question.

[BEGIN CONTEXT]
{context}
[END CONTEXT]

Question: {question}
Answer:"""
    return prompt

def ask_ollama(prompt):
    try:
        result = subprocess.run(
            ["ollama", "run", "llama3"],
            input=prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr.decode().strip()
        print(" Ollama Error:", err_msg)
        return f"Error during query processing: {err_msg}"

def ask_question(question):
    try:
        chunks = retrieve_chunks(question)
        if not chunks:
            return "No relevant content found in documents."
        prompt = format_prompt(chunks, question)
        answer = ask_ollama(prompt)
        return answer
    except FileNotFoundError as e:
        return str(e)
    except Exception as e:
        return f"Error during query processing: {e}"

if __name__ == "__main__":
    q = input("Ask a question: ")
    print(ask_question(q))
